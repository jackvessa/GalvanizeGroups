from flask import Flask, render_template, request, make_response, send_file
import numpy as np
import pandas as pd
from src.Genius_Group_Functions import *
from src.pairs_functions import *

import io
import csv
import tempfile

__author__ = 'jackvessa'

application = Flask(__name__)

@application.route('/', methods=["GET", "POST"])
def home():
    return render_template("home.html")

@application.route('/getExampleCSVs/') # this is a job for GET, not POST
def example_csvs():
    return send_file('Example_CSVs/Superhero_Single_Assignment.csv',
                     mimetype='text/csv',
                     attachment_filename='Single_Superheroes_Assignment.csv',
                     as_attachment=True)

# @application.route('/getExampleCSV/') # this is a job for GET, not POST
# def example_csv():
#     return send_file('Example_CSVs/Superhero_Single_Assignments',
#                      mimetype='text/csv',
#                      attachment_filename='Single_Superheroes_Assignment.csv',
#                      as_attachment=True)

@application.route('/getExampleCSVsfull/') # this is a job for GET, not POST
def example_csvs_full():
    return send_file('Example_CSVs/Superhero_All_Assignments.csv',
                     mimetype='text/csv',
                     attachment_filename='Full_Superheroes_Gradebook.csv',
                     as_attachment=True)

# @application.route('/getExampleCSVfull/') # this is a job for GET, not POST
# def example_csv_full():
#     return send_file('Example_CSVs/Superhero_All_Assignments.csv',
#                      mimetype='text/csv',
#                      attachment_filename='All_Superheroe_Assignments.csv',
#                      as_attachment=True)


# section_id = None
# num_groups = None
# homogeneous_bool = None
# data_frame = None
#
# file = request.files['data_file']
# if not file:
#     return "No file"
# tempfile_path = tempfile.NamedTemporaryFile().name
# file.save(tempfile_path)
# data_frame = pd.read_csv(tempfile_path, encoding='latin-1')
#
# try:
#     section_id = int(request.form["section_id"])
# except:
#     errors += "<p>{!r} is not a number!</p>\n".format(request.form["section_id"])
# try:
#     num_groups = int(request.form["num_groups"])
# except:
#     errors += "<p>{!r} is not a number!</p>\n".format(request.form["num_groups"])
# try:
#     homogeneous_bool = int(request.form["homogeneous_bool"])
# except:
#     errors += "<p>{!r} is not a number!</p>\n".format(request.form["homogeneous_bool"])
#
#
# if section_id is not None and num_groups is not None and homogeneous_bool is not None:
#     student_df = clean_file(data_frame,section_id)
#     student_df = normalize_df(student_df)
#     result = generate_optimized_groups(student_df, num_groups = num_groups,num_iter = 300, Homogeneous=homogeneous_bool)
#     groups_string = ""
#     for i,val in enumerate(result):
#         groups_string += "<br/>Group " + str(i+1) + ":<br/>"
#         groups_string += str(list(val)) + "<br/>"
#         groups_string += ("Average Score: " +
#             str(round((np.mean(student_df.loc[val]['score']))*100,2)) +"%<br/>")
#         groups_string += ("Score Range: " +
#             str(round((np.max(student_df.loc[val]['score'])-np.min(student_df.loc[val]['score']))*100,2)) +"%<br/>")

@application.route('/pairs', methods=["GET", "POST"])
def pairs():
    errors = ""

    if request.method == "POST":

        students_file = pd.read_csv(students_file)
        past_pairs_file = pd.read_csv(past_pairs)

        pairs_array = generate_pairs(students_file,past_pairs_file)

        return '''
                <html>

                    <head>
                        <link rel='stylesheet' href='/static/localrec.css'>

                        <div class = 'navBar'>

                            <a href="/" class="button">Homepage</a>

                            <a href="/cluster" class="button">Clusters</a>

                            <a href="/pairs" class="button">Pairs</a>

                            <a href="/group" class="button">Groups</a>

                        </div>

                        <title>Pairing Results</title>
                        <h1>Pairing Results</h1>


                    </head>

                    <body>

                        <p> pairs_ </p>

                    </body>

                </html>
            '''.format(pairs_ = pairs_array)
    return """
        <html>

            <head>

                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">

                <div class = 'navBar'>

                    <a href="/" class="button">Homepage</a>

                    <a href="/cluster" class="button">Clusters</a>

                    <a href="/pairs" class="button">Pairs</a>

                    <a href="/group" class="button">Groups</a>

                </div>

                <title>Generate Pairs</title>

                <link rel='stylesheet' href='/static/localrec.css'>

            </head>

            <body>
                <h1>Generate Pairs</h1>

                <h3>Choose Specifications:</h3>

                <form method="post" action = "." enctype="multipart/form-data">
                    <p>Upload student roster CSV Here:</p>
                    <input type="file" name="students_file" />

                    <p>Upload previous pairing CSV Here:</p>
                    <input type="file" name="past_pairs" />

                    <p><input type="submit" value="Submit Specifications" /></p>
                </form>

            </body>
        </html>
    """


@application.route('/group/', methods=["GET", "POST"])
def group():
    errors = ""

    if request.method == "POST":

        section_id = None
        num_groups = None
        homogeneous_bool = None
        data_frame = None

        file = request.files['data_file']
        if not file:
            return "No file"
        tempfile_path = tempfile.NamedTemporaryFile().name
        file.save(tempfile_path)
        data_frame = pd.read_csv(tempfile_path, encoding='latin-1')

        try:
            section_id = int(request.form["section_id"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["section_id"])
        try:
            num_groups = int(request.form["num_groups"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["num_groups"])
        try:
            homogeneous_bool = int(request.form["homogeneous_bool"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["homogeneous_bool"])


        if section_id is not None and num_groups is not None and homogeneous_bool is not None:
            student_df = clean_file(data_frame,section_id)
            student_df = normalize_df(student_df)
            result = generate_optimized_groups(student_df, num_groups = num_groups,num_iter = 300, Homogeneous=homogeneous_bool)
            groups_string = ""
            for i,val in enumerate(result):
                groups_string += "<br/>Group " + str(i+1) + ":<br/>"
                groups_string += str(list(val)) + "<br/>"
                groups_string += ("Average Score: " +
                    str(round((np.mean(student_df.loc[val]['score']))*100,2)) +"%<br/>")
                groups_string += ("Score Range: " +
                    str(round((np.max(student_df.loc[val]['score'])-np.min(student_df.loc[val]['score']))*100,2)) +"%<br/>")
            return '''
                <html>

                    <head>
                        <link rel='stylesheet' href='/static/localrec.css'>

                        <div class = 'navBar'>

                            <a href="/" class="button">Homepage</a>

                            <a href="/cluster" class="button">Clusters</a>

                            <a href="/pairs" class="button">Pairs</a>

                            <a href="/group" class="button">Groups</a>

                        </div>

                        <title>Genius Grouping Results (Single Assignment)</title>
                        <h1>Genius Groups (Based on Single Assignment):</h1>


                    </head>

                    <body>
                        <p> {groups_string} </p>
                        <p><a href="/">Click here to group again!</a></p>
                    </body>

                </html>
            '''.format(groups_string=groups_string)
    return """
        <html>

            <head>

                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">

                <div class = 'navBar'>

                    <a href="/" class="button">Homepage</a>

                    <a href="/cluster" class="button">Clusters</a>

                    <a href="/pairs" class="button">Pairs</a>

                    <a href="/group" class="button">Groups</a>

                </div>

                <title>Genius Grouping Setup</title>

                <link rel='stylesheet' href='/static/localrec.css'>

            </head>

            <body>
                <h1>Generate Groups</h1>

                <h3>Choose Specifications:</h3>

                <form method="post" action = "." enctype="multipart/form-data">
                    <p>Upload student roster CSV Here:</p>
                    <input type="file" name="student_file" />

                    <p>Upload previous grouping CSV Here:</p>
                    <input type="file" name="data_file" />

                    <p>Choose Number of Groups to Form:</p>
                    <input name="num_groups" />

                    <p><input type="submit" value="Submit Specifications" /></p>
                </form>

            </body>
        </html>
    """


@application.route('/group_all/', methods=["GET", "POST"])
def group_all():
    errors = ""

    if request.method == "POST":

        section_id = None
        num_groups = None
        homogeneous_bool = None
        data_frame = None

        file = request.files['data_file']
        if not file:
            return "No file"
        tempfile_path = tempfile.NamedTemporaryFile().name
        file.save(tempfile_path)
        data_frame = pd.read_csv(tempfile_path, encoding='latin-1')

        try:
            section_id = int(request.form["section_id"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["section_id"])
        try:
            num_groups = int(request.form["num_groups"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["num_groups"])
        try:
            homogeneous_bool = int(request.form["homogeneous_bool"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["homogeneous_bool"])


        if section_id is not None and num_groups is not None and homogeneous_bool is not None:
            student_df = clean_file_all_assignments(data_frame,section_id)
            student_df = normalize_df(student_df)
            result = generate_optimized_groups(student_df, num_groups = num_groups,num_iter = 300,
                Homogeneous=homogeneous_bool, criteria = 'Current Score')
            groups_string = ""
            for i,val in enumerate(result):
                groups_string += "<br/>Group " + str(i+1) + ":<br/>"
                groups_string += str(list(val)) + "<br/>"
                groups_string += ("Average Score: " +
                    str(round((np.mean(student_df.loc[val]['Current Score']))*100,2)) +"%<br/>")
                groups_string += ("Score Range: " +
                    str(round((np.max(student_df.loc[val]['Current Score'])-np.min(student_df.loc[val]['Current Score']))*100,2)) +"%<br/>")

            return '''
                <html>

                    <head>
                        <title>Genius Grouping Results</title>
                        <h1>Genius Groups (Full Gradebook):</h1>
                        <link rel="stylesheet" href="{{ url_for('static',    filename='css/style.css') }}">
                    </head>

                    <body>
                        <p> {groups_string} </p>
                        <p><a href="/">Click here to group again!</a></p>
                    </body>

                </html>
            '''.format(groups_string=groups_string)
    return """
        <html>

              <head>
                <meta charset="utf-8">
                <title>Genius Grouping Setup</title>

                <link rel="stylesheet" href="{{ url_for('static',    filename='css/style.css') }}">

              </head>

            <body>
                <h1>Generate Genius Groups (Based on Full Gradebook)!</h1>

                <h2>Choose Specifications:</h2>

                <form method="post" action = "." enctype="multipart/form-data">
                    <p>Upload the CSV Here (Full):</p>
                    <input type="file" name="data_file" />

                    <p>Enter the Section (Class Period) Here:</p>
                    <p>* For Example CSV Options are 2 or 3 *</p>
                    <p><input name="section_id" /></p>

                    <p>Choose Number of Groups to Form:</p>
                    <p><input name="num_groups" /></p>

                    <p>Enter 0 for Homogeneous (Similar) Groups  <br> or 1 for Heterogeneous (Mixed) Groups :</p>
                    <p><input name="homogeneous_bool" /></p>

                    <p><input type="submit" value="Submit Specifications" /></p>
                </form>

            </body>
        </html>
    """



@application.route('/cluster/', methods=["GET", "POST"])
def cluster():

    errors = ""

    if request.method == "POST":

        num_clusters = None

        file = request.files['data_file']
        if not file:
            return "No file"
        tempfile_path = tempfile.NamedTemporaryFile().name
        file.save(tempfile_path)

        data_frame = pd.read_csv(tempfile_path, encoding='latin-1')

        try:
            num_clusters = int(request.form["num_clusters"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["num_clusters"])

        if num_clusters is not None:
            clusters, scores = create_clusters(data_frame, num_clusters)

        cluster_strings = []

        for i in range(len(clusters)):
            name_str = ""

            for name in clusters[i][:-1]:
                name_str += name + ', '
            name_str += clusters[i][-1]

            cluster_strings.append(name_str)

        print(cluster_strings)

        master_clusters = []
        master_scores = []

        for num in range(10):
            try:
                master_clusters.append(cluster_strings[num])
            except:
                master_clusters.append(" ")

            try:
                master_scores.append("AVG Score: " + str(scores[num]) + "%")
            except:
                master_scores.append(" ")

        return '''
                <html>

                    <head>
                        <link rel='stylesheet' href='/static/localrec.css'>

                        <div class = 'navBar'>

                            <a href="/" class="button">Homepage</a>

                            <a href="/cluster" class="button">Clusters</a>

                        </div>

                        <title>Cluster Results</title>
                        <h1>Cluster Results</h1>


                    </head>

                    <body>
                        <div class = 'cluster_all_groups'>
                            <div class = 'cluster_group'
                                <p1 id = 'cluster_text'> {cluster0} </p1>
                                <p> {score0} </p>
                            </div>

                            <div class = 'cluster_group'
                                <p> {cluster1} </p>
                                <p> {score1} </p>
                            </div>

                            <div class = 'cluster_group'
                                <p> {cluster2} </p>
                                <p> {score2} </p>
                            </div>

                            <div class = 'cluster_group'
                                <p> {cluster3} </p>
                                <p> {score3} </p>
                            </div>

                            <div class = 'cluster_group'
                                <p> {cluster4} </p>
                                <p> {score4} </p>
                            </div>

                            <div class = 'cluster_group'
                                <p> {cluster5} </p>
                                <p> {score5} </p>
                            </div>

                            <div class = 'cluster_group'
                                <p> {cluster6} </p>
                                <p> {score6} </p>
                            </div>

                            <div class = 'cluster_group'
                                <p> {cluster7} </p>
                                <p> {score7} </p>
                            </div>

                            <div class = 'cluster_group'
                                <p> {cluster8} </p>
                                <p> {score8} </p>
                            </div>

                        </div>
                    </body>

                </html>
            '''.format(cluster0 = master_clusters[0], score0 = master_scores[0],
                       cluster1 = master_clusters[1], score1 = master_scores[1],
                       cluster2 = master_clusters[2], score2 = master_scores[2],
                       cluster3 = master_clusters[3], score3 = master_scores[3],
                       cluster4 = master_clusters[4], score4 = master_scores[4],
                       cluster5 = master_clusters[5], score5 = master_scores[5],
                       cluster6 = master_clusters[6], score6 = master_scores[6],
                       cluster7 = master_clusters[7], score7 = master_scores[7],
                       cluster8 = master_clusters[8], score8 = master_scores[8])
    return """
        <html>

            <head>

                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">

                <div class = 'navBar'>

                    <a href="/" class="button">Homepage</a>

                    <a href="/cluster" class="button">Clusters</a>

                </div>

                <title>Generate Clusters</title>

                <link rel='stylesheet' href='/static/localrec.css'>

            </head>

            <body>
                <h1>Generate Clusters</h1>

                <h3>Choose Specifications:</h3>

                <form method="post" action = "." enctype="multipart/form-data">
                    <p>Upload student roster CSV Here:</p>
                    <input type="file" name="data_file" />

                    <p>Choose Number of Clusters to Form:</p>
                    <p><input name="num_clusters" type = "number" min = "2" max = "9" autocomplete='off'></p>

                    <p><input type="submit" value="Submit Specifications" /></p>
                </form>

            </body>
        </html>
    """


# <p>Upload previous pairing CSV Here:</p>
# <input type="file" name="past_pairs" />






    # errors = ""
    #
    # if request.method == "POST":
    #
    #     section_id = None
    #     num_clusters = None
    #     data_frame = None
    #
    #     file = request.files['data_file']
    #     if not file:
    #         return "No file"
    #     tempfile_path = tempfile.NamedTemporaryFile().name
    #     file.save(tempfile_path)
    #     data_frame = pd.read_csv(tempfile_path, encoding='latin-1')
    #
    #     try:
    #         section_id = int(request.form["section_id"])
    #     except:
    #         errors += "<p>{!r} is not a number!</p>\n".format(request.form["section_id"])
    #     try:
    #         num_clusters = int(request.form["num_clusters"])
    #     except:
    #         errors += "<p>{!r} is not a number!</p>\n".format(request.form["num_clusters"])
    #
    #     if section_id is not None and num_clusters is not None:
    #         student_df = clean_file(data_frame,section_id)
    #         student_df = normalize_df(student_df)
    #         student_df = add_clusters(student_df, num_clusters = num_clusters)
    #         result = return_cluster_list(student_df, num_clusters)
    #         groups_string = ""
    #         for i,val in enumerate(result):
    #             groups_string += "<br/>Cluster " + str(i+1) + ":<br/>"
    #             groups_string += str(list(val)) + "<br/>"
    #             groups_string += ("Average Score: " +
    #                 str(round(np.mean(student_df.loc[val]['score'])*100,2)) +"%<br/>")
    #         return '''
    #             <html>
    #
    #                 <head>
    #                     <h1>Genius Clusters:</h1>
    #                 </head>
    #
    #                 <body>
    #                     <p> {groups_string} </p>
    #                     <p><a href="/">Click here to cluster again!</a></p>
    #                 </body>
    #
    #             </html>
    #         '''.format(groups_string=groups_string)
    # return """
    #     <html>
    #         <body>
    #             <h1>Generate Genius Clusters (Single Assignment)!</h1>
    #
    #             <h2>Choose Specifications:</h2>
    #
    #             <form method="post" action = "." enctype="multipart/form-data">
    #                 <p>Upload the CSV Here (Single):</p>
    #                 <input type="file" name="data_file" />
    #
    #                 <p>Enter the Section (Class Period) Here:</p>
    #                 <p>* For Example CSV Options are 4 or 6 *</p>
    #                 <p><input name="section_id" /></p>
    #
    #                 <p>Choose Number of Clusters to Form:</p>
    #                 <p><input name="num_clusters" /></p>
    #
    #                 <p><input type="submit" value="Submit Specifications" /></p>
    #             </form>
    #
    #         </body>
    #     </html>
    # """


@application.route('/cluster_all/', methods=["GET", "POST"])
def cluster_all():
    errors = ""

    if request.method == "POST":

        section_id = None
        num_clusters = None
        data_frame = None

        file = request.files['data_file']
        if not file:
            return "No file"
        tempfile_path = tempfile.NamedTemporaryFile().name
        file.save(tempfile_path)
        data_frame = pd.read_csv(tempfile_path, encoding='latin-1')

        try:
            section_id = int(request.form["section_id"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["section_id"])
        try:
            num_clusters = int(request.form["num_clusters"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["num_clusters"])

        if section_id is not None and num_clusters is not None:
            student_df = clean_file_all_assignments(data_frame,section_id)
            student_df = normalize_df(student_df)
            student_df = add_clusters(student_df, num_clusters = num_clusters)
            result = return_cluster_list(student_df, num_clusters)
            groups_string = ""
            for i,val in enumerate(result):
                groups_string += "<br/>Cluster " + str(i+1) + ":<br/>"
                groups_string += str(list(val)) + "<br/>"
                groups_string += ("Average Score: " +
                    str(round(np.mean(student_df.loc[val]['Current Score'])*100,2)) +"%<br/>")

            return '''
                <html>

                    <head>
                        <h1>Genius Clusters (Full Gradebook):</h1>
                    </head>

                    <body>
                        <p> {groups_string} </p>
                        <p><a href="/">Click here to cluster again!</a></p>
                    </body>

                </html>
            '''.format(groups_string=groups_string)
    return """
        <html>
            <body>
                <h1>Generate Genius Clusters (Full Gradebook)!</h1>

                <h2>Choose Specifications:</h2>

                <form method="post" action = "." enctype="multipart/form-data">
                    <p>Upload the CSV Here:</p>
                    <input type="file" name="data_file" />

                    <p>Enter the Section (Class Period) Here:</p>
                    <p>* For Example CSV Options are 2 or 3 *</p>
                    <p><input name="section_id" /></p>

                    <p>Choose Number of Clusters to Form:</p>
                    <p><input name="num_clusters" /></p>

                    <p><input type="submit" value="Submit Specifications" /></p>
                </form>

            </body>
        </html>
    """


@application.route('/galvanize/', methods=["GET", "POST"])
def galvanize():
    errors = ""

    if request.method == "POST":

        num_groups = None
        homogeneous_bool = None
        data_frame = None

        file = request.files['data_file']
        if not file:
            return "No file"
        tempfile_path = tempfile.NamedTemporaryFile().name
        file.save(tempfile_path)
        data_frame = pd.read_csv(tempfile_path, encoding='latin-1')

        try:
            num_groups = int(request.form["num_groups"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["num_groups"])
        try:
            homogeneous_bool = int(request.form["homogeneous_bool"])
        except:
            errors += "<p>{!r} is not a number!</p>\n".format(request.form["homogeneous_bool"])


        if num_groups is not None and homogeneous_bool is not None:
            student_df = clean_file_galvanize(data_frame)
            # student_df = normalize_df(data_frame)

            result = generate_optimized_groups(student_df, num_groups = num_groups,num_iter = 300, Homogeneous=homogeneous_bool,criteria='Overall Average')
            groups_string = ""

            for i,val in enumerate(result):
                groups_string += "<br/>Group " + str(i+1) + ":<br/>"
                groups_string += str(list(val)) + "<br/>"
                groups_string += ("Average Score: " +
                    str(round((np.mean(student_df.loc[val]['Overall Average']))*100,2)) +"%<br/>")
                groups_string += ("Score Range: " +
                    str(round((np.max(student_df.loc[val]['Overall Average'])-np.min(student_df.loc[val]['Overall Average']))*100,2)) +"%<br/>")
            return '''
                <html>

                    <head>
                        <title>Genius Grouping Results (Galvanize)</title>
                        <h1>Genius Groups (Galvanize):</h1>
                        <link rel="stylesheet" href="{{ url_for('static',    filename='css/style.css') }}">
                    </head>

                    <body>
                        <p> {groups_string} </p>
                        <p><a href="/">Click here to group again!</a></p>
                    </body>

                </html>
            '''.format(groups_string=groups_string)
    return """
        <html>
            <link rel="stylesheet" href="{{ url_for('static',    filename='css/style.css') }}">

              <head>
                <meta charset="utf-8">
                <title>Genius Grouping Setup</title>

                <link rel="stylesheet" href="{{ url_for('static',    filename='css/style.css') }}">

              </head>

            <body>
                <h1>Generate Genius Groups (Based on Single Assignment)!</h1>

                <h2>Choose Specifications:</h2>

                <form method="post" action = "." enctype="multipart/form-data">
                    <p>Upload the CSV Here (student_name & score columns):</p>
                    <input type="file" name="data_file" />

                    <p>Choose Number of Groups to Form:</p>
                    <p><input name="num_groups" /></p>

                    <p>Enter 0 for Homogeneous (Similar) Groups  <br> or 1 for Heterogeneous (Mixed) Groups :</p>
                    <p><input name="homogeneous_bool" /></p>

                    <p><input type="submit" value="Submit Specifications" /></p>
                </form>

            </body>
        </html>
    """


if __name__ == "__main__":
    application.run(debug=True)
