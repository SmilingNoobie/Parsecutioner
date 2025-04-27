
 Parsecutioner - CV Parser, Analyzer, and Advisor

Parsecutioner is a powerful tool designed for both recruiters and developers to optimize and analyze CVs based on job descriptions. Built using natural language processing (NLP) and machine learning techniques, this app helps recruiters efficiently rank resumes and provides actionable feedback to job seekers on how to improve their CVs for specific roles.

 Features

- **CV Parsing and Ranking:** Automatically parses resumes and compares them to job descriptions using tokenization, embeddings, and cosine similarity. The result is a score that ranks the CV from ‘Matchmaker Needed’ to ‘Perfect Fit.’
  
- **Job Description Alignment:** The app highlights missing skills and suggests improvements to ensure the CV aligns better with the job description.
  
- **Interview Question Generation:** Based on the CV and job description gaps, the app can generate interview questions to assess the applicant's suitability.

- **Batch Processing:** Parsecutioner can process up to 20 resumes at once, making it efficient for recruiters managing multiple applicants.

- **Real-time Feedback:** Instant insights for both recruiters (to assess candidates) and developers (to tweak resumes based on job descriptions).

#Technologies Used

- **Python**
- **Streamlit** for the web interface
- **Sentence-Transformer** for embeddings
- **NLTK** for text normalization and tokenization
- **Cosine Similarity** for comparing job descriptions and resumes
- **Machine Learning** for ranking and analysis

Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/SmilingNoobie/parsecutioner.git
    ```

2. Navigate to the project directory:
    ```bash
    cd parsecutioner
    ```

3. Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'
    ```

4. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

5. Run the app:
    ```bash
    streamlit run app.py
    ```

How it works

- **Parsing and Tokenization:** The app tokenizes the job description and CVs using NLTK to clean and extract meaningful information.
  
- **Vectorization:** Sentence-Transformer converts both job descriptions and CVs into embeddings (vectors) for more accurate comparison.

- **Scoring System:** We use cosine similarity to measure the relevance of each CV to the job description. The score is calculated using a weighted system for different sections like skills, experience, and education.

- **Batch Processing:** The app can handle up to 20 resumes simultaneously, allowing recruiters to process multiple CVs at once.

Usage

- **For Recruiters:** Upload job descriptions and CVs, and receive an analysis of each resume's fit for the position. Get ranked results and feedback on missing skills.

- **For Developers:** Upload your CV and a job description, and receive suggestions for improvements and optimized keywords to enhance your chances of landing the job.

Challenges Overcome

- **Time Efficiency:** The app is optimized to handle up to 20 resumes at once without compromising speed or performance.
  
- **Accuracy:** Tuning the machine learning models to provide more accurate rankings and relevant feedback was key to delivering a useful experience for both recruiters and developers.

- **User Experience:** Building an intuitive interface with Streamlit allowed us to present complex NLP results in a simple, easy-to-use format.

Future Improvements

- **AI-Powered Recommendations:** Improve the algorithm to suggest even more tailored resume improvements.
  
- **Broader Job Role Compatibility:** Add more job descriptions and role-specific recommendations for even better alignment.

- **Mobile Compatibility:** Develop a mobile version for recruiters and developers to access the app on the go.

Contributing

Feel free to fork this repository, make changes, and submit pull requests. Contributions are always welcome!

License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

