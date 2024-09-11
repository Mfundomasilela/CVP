import streamlit as st
import pandas as pd
import base64
import random
import time
import io
import os
import datetime
from pyresparser import ResumeParser
from pdfminer.high_level import extract_text
from PIL import Image
from streamlit_tags import st_tags
import nltk

# Ensure stopwords are downloaded
try:
    nltk.data.find('corpora/stopwords.zip')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))

# Define CSV file path
CSV_FILE_PATH = 'user_data.csv'

# ... rest of the code remains the same ...


def save_to_csv(data):
    df = pd.DataFrame(data, columns=['Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page', 
                                     'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills', 
                                     'Recommended Course'])
    df.to_csv(CSV_FILE_PATH, mode='a', header=not os.path.exists(CSV_FILE_PATH), index=False)

def pdf_reader(file):
    return extract_text(file)

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 🎓**")
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        st.markdown(f"• [{c_name}]({c_link})")
        rec_course.append(c_name)
        if len(rec_course) == no_of_reco:
            break
    return rec_course

# Course lists
ds_course = [
    ('TensorFlow Certification', 'https://www.coursera.org/learn/intro-to-tensorflow'),
    ('Data Science Specialization', 'https://www.coursera.org/specializations/jhu-data-science'),
]

web_course = [
    ('Full Stack Web Development', 'https://www.udemy.com/course/the-web-developer-bootcamp/'),
    ('JavaScript Web Development', 'https://www.codecademy.com/learn/introduction-to-javascript'),
]

android_course = [
    ('Android Development for Beginners', 'https://www.udemy.com/course/complete-android-n-developer-course/'),
    ('Flutter & Dart - The Complete Guide', 'https://www.udemy.com/course/flutter-dart-the-complete-guide/'),
]

ios_course = [
    ('iOS 16 Programming for Beginners', 'https://www.udemy.com/course/ios-16-development/'),
    ('SwiftUI Masterclass', 'https://www.udemy.com/course/swiftui-masterclass-course/'),
]

uiux_course = [
    ('UI/UX Design Specialization', 'https://www.coursera.org/specializations/ui-ux-design'),
    ('UX & Web Design Master Course', 'https://www.udemy.com/course/ux-web-design-master-course/'),
]

def run():
    img = Image.open('./Logo/pexels-vojtech-okenka-127162-392018.jpg')
    st.image(img)
    st.title("Talent Acquisition Assistant!")
    st.sidebar.markdown("# Please select an Option")
    activities = ["User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    link = '[©Developed by Mfundo](https://www.linkedin.com/in/nomfundo-masilela-638bb3218?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3BlJMn04CbRdaLQlphkDs5Nw%3D%3D)'
    st.sidebar.markdown(link, unsafe_allow_html=True)

    if choice == 'User':
        st.markdown('''<h5 style='text-align: left; color: #021659;'>Upload your resume, and get smart recommendations</h5>''', unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Uploading your Resume...'):
                time.sleep(2)
            save_image_path = f'./Uploaded_Resumes/{pdf_file.name}'
            os.makedirs(os.path.dirname(save_image_path), exist_ok=True)
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                resume_text = pdf_reader(save_image_path)

                st.header("**Resume Analysis**")
                st.success(f"Hello {resume_data.get('name', 'User')}")
                st.subheader("**Your Basic Info**")
                st.text(f"Name: {resume_data.get('name', 'N/A')}")
                st.text(f"Email: {resume_data.get('email', 'N/A')}")
                st.text(f"Contact: {resume_data.get('mobile_number', 'N/A')}")
                st.text(f"Resume pages: {resume_data.get('no_of_pages', 'N/A')}")

                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = "Fresher"
                    st.markdown('<h4 style="text-align: left; color: #d73b5c;">You are at Fresher level!</h4>', unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = "Intermediate"
                    st.markdown('<h4 style="text-align: left; color: #1ed760;">You are at Intermediate level!</h4>', unsafe_allow_html=True)
                elif resume_data['no_of_pages'] >= 3:
                    cand_level = "Experienced"
                    st.markdown('<h4 style="text-align: left; color: #fba171;">You are at Experienced level!</h4>', unsafe_allow_html=True)

                keywords = st_tags(label='### Your Current Skills',
                                   text='See our skills recommendation below',
                                   value=resume_data.get('skills', []), key='1')

                ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask', 'streamlit']
                web_keyword = ['react', 'django', 'node js', 'react js', 'php', 'laravel', 'magento', 'wordpress', 'javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
                ios_keyword = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode']
                uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes', 'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator', 'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro', 'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp', 'user research', 'user experience']

                recommended_skills = []
                reco_field = ''
                rec_course = []

                for i in resume_data.get('skills', []):
                    if i.lower() in ds_keyword:
                        reco_field = 'Data Science'
                        st.success("**Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling', 'Data Mining', 'Clustering & Classification', 'Data Analytics', 'Quantitative Analysis', 'Web Scraping', 'ML Algorithms', 'Keras', 'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow', 'Flask', 'Streamlit']
                        st_tags(label='### Recommended Skills for You', text='Recommended skills generated from System', value=recommended_skills, key='2')
                        st.markdown('<h4 style="text-align: left; color: #1ed760;">Adding these skills to your resume will boost🚀 the chances of getting a Job</h4>', unsafe_allow_html=True)
                        rec_course = course_recommender(ds_course)
                        break

                    elif i.lower() in web_keyword:
                        reco_field = 'Web Development'
                        st.success("**Our analysis says you are looking for Web Development Jobs**")
                        recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'PHP', 'Laravel', 'Magento', 'WordPress', 'JavaScript', 'Angular JS', 'C#', 'Flask', 'SDK']
                        st_tags(label='### Recommended Skills for You', text='Recommended skills generated from System', value=recommended_skills, key='3')
                        st.markdown('<h4 style="text-align: left; color: #1ed760;">Adding these skills to your resume will boost🚀 the chances of getting a Job💼</h4>', unsafe_allow_html=True)
                        rec_course = course_recommender(web_course)
                        break

                    elif i.lower() in android_keyword:
                        reco_field = 'Android Development'
                        st.success("**Our analysis says you are looking for Android App Development Jobs**")
                        recommended_skills = ['Android', 'Android development', 'Flutter', 'Kotlin', 'XML', 'Java', 'Kivy']
                        st_tags(label='### Recommended Skills for You', text='Recommended skills generated from System', value=recommended_skills, key='4')
                        st.markdown('<h4 style="text-align: left; color: #1ed760;">Adding these skills to your resume will boost🚀 the chances of getting a Job</h4>', unsafe_allow_html=True)
                        rec_course = course_recommender(android_course)
                        break

                    elif i.lower() in ios_keyword:
                        reco_field = 'iOS Development'
                        st.success("**Our analysis says you are looking for iOS Development Jobs**")
                        recommended_skills = ['iOS', 'iOS development', 'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode']
                        st_tags(label='### Recommended Skills for You', text='Recommended skills generated from System', value=recommended_skills, key='5')
                        st.markdown('<h4 style="text-align: left; color: #1ed760;">Adding these skills to your resume will boost🚀 the chances of getting a Job</h4>', unsafe_allow_html=True)
                        rec_course = course_recommender(ios_course)
                        break

                    elif i.lower() in uiux_keyword:
                        reco_field = 'UI/UX Design'
                        st.success("**Our analysis says you are looking for UI/UX Design Jobs**")
                        recommended_skills = ['UX', 'Adobe XD', 'Figma', 'Zeplin', 'Balsamiq', 'UI', 'Prototyping', 'Wireframes', 'Storyframes', 'Adobe Photoshop', 'Photoshop', 'Editing', 'Adobe Illustrator', 'Illustrator', 'Adobe After Effects', 'After Effects', 'Adobe Premier Pro', 'Premier Pro', 'Adobe InDesign', 'InDesign', 'Wireframe', 'Solid', 'Grasp', 'User Research', 'User Experience']
                        st_tags(label='### Recommended Skills for You', text='Recommended skills generated from System', value=recommended_skills, key='6')
                        st.markdown('<h4 style="text-align: left; color: #1ed760;">Adding these skills to your resume will boost🚀 the chances of getting a Job</h4>', unsafe_allow_html=True)
                        rec_course = course_recommender(uiux_course)
                        break

                # Save data to CSV
                save_to_csv([[
                    resume_data.get('name', 'N/A'),
                    resume_data.get('email', 'N/A'),
                    resume_data.get('resume_score', 'N/A'),
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    resume_data.get('no_of_pages', 'N/A'),
                    reco_field,
                    cand_level,
                    ', '.join(resume_data.get('skills', [])),
                    ', '.join(recommended_skills),
                    ', '.join(rec_course)
                ]])

if __name__ == "__main__":
    run()
