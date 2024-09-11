import streamlit as st
import pandas as pd
import base64
import random
import time
import datetime
import nltk
import os
import yt_dlp
from PIL import Image
import pymysql
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io
from streamlit_tags import st_tags
import plotly.express as px

# Download NLTK stopwords
nltk.download('stopwords')

# Replace pafy with yt-dlp
def fetch_yt_video(video_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        return info_dict.get('title', 'No title found')

def fetch_yt_videos(link):
    info = fetch_yt_video(link)
    return info

def get_table_download_link(df, filename, text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in: dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 🎓**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

# CONNECT TO DATABASE
try:
    connection = pymysql.connect(host='localhost', user='root', password='Mfundo@01', db='cv')
except pymysql.MySQLError as e:
    st.error(f"Error connecting to MySQL Database: {e}")
connection = pymysql.connect(host='localhost', user='root', password='Mfundo@01', db='cv')
cursor = connection.cursor()

def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    DB_table_name = 'user_data'
    insert_sql = f"INSERT INTO {DB_table_name} VALUES (0, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    rec_values = (name, email, str(res_score), timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills, courses)
    cursor.execute(insert_sql, rec_values)
    connection.commit()

st.set_page_config(
    page_title="Talent Acquisition Assistant!",
    page_icon='./Logo/pexels-vojtech-okenka-127162-392018.jpg',
)

def run():
    img = Image.open('./Logo/pexels-vojtech-okenka-127162-392018.jpg')
    st.image(img)
    st.title("Talent Acquisition Assistant!")
    st.sidebar.markdown("# Please select an Option")
    activities = ["User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    link = '[©Developed by Mfundo](https://www.linkedin.com/in/nomfundo-masilela-638bb3218?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3BlJMn04CbRdaLQlphkDs5Nw%3D%3D)'
    st.sidebar.markdown(link, unsafe_allow_html=True)

    # Create the DB
    db_sql = "CREATE DATABASE IF NOT EXISTS CV;"
    cursor.execute(db_sql)

    # Create table
    DB_table_name = 'user_data'
    table_sql = f"""
    CREATE TABLE IF NOT EXISTS {DB_table_name} (
        ID INT NOT NULL AUTO_INCREMENT,
        Name VARCHAR(500) NOT NULL,
        Email_ID VARCHAR(500) NOT NULL,
        resume_score VARCHAR(8) NOT NULL,
        Timestamp VARCHAR(50) NOT NULL,
        Page_no VARCHAR(5) NOT NULL,
        Predicted_Field BLOB NOT NULL,
        User_level BLOB NOT NULL,
        Actual_skills BLOB NOT NULL,
        Recommended_skills BLOB NOT NULL,
        Recommended_courses BLOB NOT NULL,
        PRIMARY KEY (ID)
    );
    """
    cursor.execute(table_sql)

    if choice == 'User':
        st.markdown('''<h5 style='text-align: left; color: #021659;'> Upload your resume, and get smart recommendations</h5>''',
                    unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Uploading your Resume...'):
                time.sleep(4)
            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                resume_text = pdf_reader(save_image_path)

                st.header("**Resume Analysis**")
                st.success("Hello " + resume_data['name'])
                st.subheader("**Your Basic info**")
                try:
                    st.text('Name: ' + resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: ' + str(resume_data['no_of_pages']))
                except:
                    pass

                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''', unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''', unsafe_allow_html=True)
                elif resume_data['no_of_pages'] >= 3:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!</h4>''', unsafe_allow_html=True)

                # Skills recommendation
                keywords = st_tags(label='### Your Current Skills',
                                   text='See our skills recommendation below',
                                   value=resume_data['skills'], key='1')

                # Keywords for various fields
                ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep Learning', 'flask', 'streamlit']
                web_keyword = ['react', 'django', 'node js', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                               'javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
                ios_keyword = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode']
                uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes',
                                'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator', 'illustrator',
                                'adobe after effects', 'after effects', 'adobe premier pro', 'premier pro', 'adobe indesign',
                                'indesign', 'wireframe', 'solid', 'grasp', 'user research', 'user experience']

                recommended_skills = []
                reco_field = ''
                rec_course = ''

                # Courses recommendation
                for i in resume_data['skills']:
                    if i.lower() in ds_keyword:
                        reco_field = 'Data Science'
                        rec_course = [("Deep Learning Specialization", "https://www.coursera.org/specializations/deep-learning"),
                                      ("Machine Learning by Andrew Ng", "https://www.coursera.org/learn/machine-learning"),
                                      ("Python for Data Science and Machine Learning Bootcamp", "https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/"),
                                      ("Data Science MicroMasters", "https://www.edx.org/micromasters/uc-san-diego-data-science"),
                                      ("Data Analyst Nanodegree", "https://www.udacity.com/course/data-analyst-nanodegree--nd002")]
                        break
                    elif i.lower() in web_keyword:
                        reco_field = 'Web Development'
                        rec_course = [("The Complete Web Developer Bootcamp", "https://www.udemy.com/course/the-complete-web-developer-bootcamp/"),
                                      ("The Web Developer Bootcamp 2024", "https://www.udemy.com/course/the-web-developer-bootcamp/"),
                                      ("Front-End Web Developer Nanodegree", "https://www.udacity.com/course/front-end-web-developer-nanodegree--nd0011"),
                                      ("Full Stack Web Developer Nanodegree", "https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044"),
                                      ("JavaScript Algorithms and Data Structures", "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/")]
                        break
                    elif i.lower() in android_keyword:
                        reco_field = 'Android Development'
                        rec_course = [("Android App Development for Beginners", "https://www.udemy.com/course/android-app-development-for-beginners/"),
                                      ("Master Android App Development with Kotlin", "https://www.udemy.com/course/master-android-app-development-with-kotlin/"),
                                      ("The Complete Android App Developer Bootcamp", "https://www.udemy.com/course/the-complete-android-app-developer-bootcamp/"),
                                      ("Advanced Android App Development", "https://www.udacity.com/course/advanced-android-app-development--ud855"),
                                      ("Android Development with Java", "https://www.coursera.org/learn/android-app-development")]
                        break
                    elif i.lower() in ios_keyword:
                        reco_field = 'iOS Development'
                        rec_course = [("iOS 16 Programming for Beginners", "https://www.udemy.com/course/ios-16-programming-for-beginners/"),
                                      ("The Complete iOS App Development Bootcamp", "https://www.udemy.com/course/the-complete-ios-app-development-bootcamp/"),
                                      ("iOS Development with Swift", "https://www.coursera.org/learn/ios-development-swift"),
                                      ("Mastering iOS Development", "https://www.udacity.com/course/mastering-ios-development--ud879"),
                                      ("iOS App Development Fundamentals", "https://www.pluralsight.com/courses/ios-app-development-fundamentals")]
                        break
                    elif i.lower() in uiux_keyword:
                        reco_field = 'UI/UX Design'
                        rec_course = [("The UI/UX Design Specialization", "https://www.coursera.org/specializations/ui-ux-design"),
                                      ("User Experience Design Fundamentals", "https://www.udemy.com/course/user-experience-design-fundamentals/"),
                                      ("UX & Web Design Master Course", "https://www.udemy.com/course/ux-web-design-master-course/"),
                                      ("UI/UX Design Nanodegree", "https://www.udacity.com/course/ui-ux-designer-nanodegree--nd578"),
                                      ("Mastering UI Design", "https://www.pluralsight.com/courses/mastering-ui-design")]
                        break
                    else:
                        reco_field = 'General'
                        rec_course = [("The Complete Web Developer Bootcamp", "https://www.udemy.com/course/the-complete-web-developer-bootcamp/"),
                                      ("The Complete Data Science Bootcamp", "https://www.udemy.com/course/the-complete-data-science-bootcamp/"),
                                      ("The Complete Android App Developer Bootcamp", "https://www.udemy.com/course/the-complete-android-app-developer-bootcamp/"),
                                      ("The Complete iOS App Development Bootcamp", "https://www.udemy.com/course/the-complete-ios-app-development-bootcamp/"),
                                      ("The Complete UI/UX Design Bootcamp", "https://www.udemy.com/course/the-complete-uiux-design-bootcamp/")]
                        break

                st.subheader("**Skill Recommendations 🛠️**")
                st.write(f"Based on your skills, we recommend exploring the following area: **{reco_field}**")

                # Recommend courses
                rec_courses = course_recommender(rec_course)

                st.subheader("**Recommended Courses 📚**")
                st.write("Explore these courses to enhance your skills:")
                for course in rec_courses:
                    st.write(course)

                # Insert data into database
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                insert_data(resume_data['name'], resume_data['email'], resume_data.get('score', 'N/A'),
                            timestamp, resume_data['no_of_pages'], reco_field, cand_level, 
                            ', '.join(resume_data.get('skills', [])), ', '.join(recommended_skills), ', '.join(rec_courses))

    elif choice == 'Admin':
        st.subheader("**Admin Dashboard**")
        st.write("View and manage the data from user uploads.")

        query = "SELECT * FROM user_data;"
        cursor.execute(query)
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=['ID', 'Name', 'Email_ID', 'resume_score', 'Timestamp', 'Page_no',
                                           'Predicted_Field', 'User_level', 'Actual_skills', 'Recommended_skills', 
                                           'Recommended_courses'])
        st.write(df)
        st.markdown(get_table_download_link(df, 'user_data.csv', 'Download CSV'), unsafe_allow_html=True)

run()
