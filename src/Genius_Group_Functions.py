import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
# Imports for NLP Analysis of Columns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import text
from sklearn.cluster import KMeans

# Create Group Sizes
def calc_group_sizes(num_students, num_groups):
    '''
    Parameters
    -----------
    num_students : int
        Number of students in the class
    num_groups : int
        Number of groups to break students into

    Returns
    ---------
    group_size : List of ideal group sizes
    '''
    group_sizes = []

    class_size = int(num_students)
    group_num_count = int(num_groups)
    group_num = int(num_groups)

    for i in range(group_num_count):
        temp = class_size // group_num
        class_size -= temp
        group_num -= 1
        group_sizes.append(temp)

    return group_sizes

# Clean DataFrame by Section
def clean_file(dataframe):
    '''
    Clean CSV file
    --------------------

    Parameters
    -----------
    .csv file :

    Returns
    ---------
    Pandas DataFrame (Cleaned)
    '''
    df = dataframe.copy()
    df.set_index(keys=df['FIRST'],inplace=True)

    try:
        df.drop(columns=['FIRST','LAST','GITHUB','Class Rank','Overall Average'],inplace=True)
    except:
        pass

    for col in df.columns:
        df[col] = df[col].str.rstrip('%').astype('float') / 100.0

    return df

# def clean_file_galvanize(df):
#     '''
#     '''
#     temp_df = df.copy()
#     temp_df.drop(columns=['LAST', 'GITHUB','Class Rank'], inplace=True)

#     temp_df.set_index('FIRST', inplace=True)

#     for col in temp_df.columns:

#         temp_df[col] = temp_df[col].apply(lambda x: float((str(x).replace("%",""))))

#     return temp_df

# Normalize DataFrame (0-1)
def normalize_df(df):
    '''
    Normalize DataFrame Values from 0-1

    Parameters
    ----------
    df : DataFrame to Normalize

    Returns
    -------
    Normalized DataFrame
    '''
    return df.apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)) \
        if np.min(x) != np.max(x) else x)

# Add Cluster Column to DataFrame
def add_clusters(df, num_clusters=6):
    '''
    Add Clusters
    '''
    kmeans = KMeans(num_clusters)
    kmeans.fit(df)
    cluster = kmeans.predict(df)
    df['Cluster'] = cluster
    return df


def create_clusters(assessment_df, num_clusters = 3):
    results_array = []
    student_dict = dict()
    cluster_averages = dict()

    student_df = clean_file(assessment_df)
    student_df = normalize_df(student_df)
    student_df = add_clusters(student_df, num_clusters = num_clusters)
    results_array.append(student_df)

    result = return_cluster_list(student_df, num_clusters = num_clusters)
    results_array.append(result)

    for i,val in enumerate(result):
        avg = round(np.mean(np.mean(student_df.loc[val].iloc[:,:-1]).values)*100, 2)
        student_dict[i] = val
        cluster_averages[i] = avg

    results_array.append(student_dict)
    results_array.append(cluster_averages)

    clusters, scores = generate_clusters_and_scores(results_array)

    return clusters, scores

# Return a list of Clusters
def return_cluster_list(df,num_clusters=6):
    '''
    Return a List of Clustered Students
    '''
    cluster_list = []

    for i in range(num_clusters):
        cluster_list.append(list(df[df['Cluster']==i].index))

    return cluster_list

def generate_clusters_and_scores(temp_arr):

    cluster_students_array = []
    cluster_students_scores_array = []

    for key, cluster in temp_arr[2].items():
        cluster_students_array.append(cluster)

    for key, score in temp_arr[3].items():
        cluster_students_scores_array.append(score)

    return cluster_students_array, cluster_students_scores_array


# Generate Optimized Group (Based on Residual Sum of Squares)
def generate_optimized_groups(student_df, num_iter = 100, num_groups = 6, Homogeneous = 0, criteria = 'score'):
    '''

    Parameters
    ----------
    student_df : DataFrame with student names as index and score column
    num_iter : int
        Number of Iterations to run loss function
    num_groups : int
        Number of groups to divide students into
    Homogeneous : bool
        If True, create Homogeneous (similar) groups.
        If False, create Heterogeneous (different) groups

    Returns
    -------
    Optimal Groups
    '''
    index_list = list(student_df.index)

    if Homogeneous == 0:
        ideal_loss = 9999
    elif Homogeneous == 1:
        ideal_loss = 0
    num_students = len(student_df)

    size_list = calc_group_sizes(num_students,num_groups)

    for i in range(num_iter):
        randomized_index_list = np.random.choice(index_list, size = len(index_list),replace=False)
        group_set = set({})
        index_track = 0
        total_loss = 0

        for num in size_list:
            j = frozenset(randomized_index_list[0 + index_track:index_track+num])
            group_set.add(j)
            index_track += num

        for group in group_set:
            unfrozen = set(group)
            group_loss = 0
            avg_score = np.mean(student_df.loc[unfrozen][criteria])

            for s in range(len(group)):
                group_loss += (student_df.loc[unfrozen][criteria][s] - avg_score) ** 2

            total_loss += group_loss

        if Homogeneous == 0 and total_loss < ideal_loss:
            ideal_loss = total_loss
            best_group = group_set
            print("New Best Homogeneous Group Loss:", ideal_loss)

        elif Homogeneous == 1 and total_loss > ideal_loss:
            ideal_loss = total_loss
            best_group = group_set
            print("New Best Heterogeneous Group Loss:", ideal_loss)

    print("\n")
    print("Final Best Group Loss:", ideal_loss)
    print("Final Best Grouping:\n")


    for i,g in enumerate(best_group):
        print("Group",i+1)
        print(student_df.loc[set(g)][criteria],"\n")

    return best_group


# Make Student Strength/Growth Areas DataFrame
def make_student_growth_and_strength_df(df_original,sectionID,cluster_labels):
    '''
    Create a DataFrame that includes students strengths and growth areas for question clusters

    Return a List of Clustered Students

    Parameters
    ----------
    df : Pandas DataFrame
    sectionID : Section Number for Students

    Returns
    -------
    Pandas DataFrame with strengths and growth areas for question clusters

    '''
    df = df_original.copy()
    clean_df = clean_file(df,sectionID)
    quest_num_df = clean_df.iloc[:,0:-3]
    quest_num_df.columns = cluster_labels
    quest_num_df_grouped = quest_num_df.groupby(quest_num_df.columns, axis=1).sum()
    grouped_quest_normed_df = normalize_df(quest_num_df_grouped)

    x = grouped_quest_normed_df.copy().ix[0]
    x.index[x.argmin()]
    min_list, max_list = [], []

    for i in range (len(grouped_quest_normed_df)):
        x = grouped_quest_normed_df.ix[i]

        min_list.append(x.index[x.argmin()])
        max_list.append(x.index[x.argmax()])


    grouped_quest_normed_df['Strength Area'] = max_list
    grouped_quest_normed_df['Growth Area'] = min_list

    return grouped_quest_normed_df


# Generate Growth Areas Groups
def generate_growth_groups(df,num_groups):
    '''

    Parameters
    ----------
    student_df : DataFrame with student names as index and Strength/Growth Areas included

    Returns
    -------
    Growth Area Groups
    '''
    index_list = list(df.index)

    cluster_focus = []

    for i in range(num_groups):

        cluster_focus.append(list(df[df['Growth Area']==i].index))

    print("Grouping by Growth Areas:\n")

    for i,g in enumerate(cluster_focus):
        print("Group",i+1)
        print(str(g)+"\n")

    return cluster_focus


# Generate Strength Areas Groups
def generate_strength_groups(df,num_groups):
    '''

    Parameters
    ----------
    student_df : DataFrame with student names as index and Strength/Growth Areas included

    Returns
    -------
    Growth Area Groups
    '''
    index_list = list(df.index)

    cluster_focus = []

    for i in range(num_groups):

        cluster_focus.append(list(df[df['Strength Area']==i].index))

    print("Grouping by Strength Areas:\n")

    for i,g in enumerate(cluster_focus):
        print("Group",i+1)
        print(str(g)+"\n")

    return cluster_focus
