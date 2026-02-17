# Dynamic Quiz Loader

## Features

### Core Features
- **Dynamic Quiz Loading**: automatically detects and loads all CSV quiz files from the project directory
- **Multiple Quiz Topics**
- **Interactive UI**: responsive interface with shuffled answer options
- **Practice Mode**: review and practice only the questions you got wrong
- **Exam Mode**: simulated exams with 33 questions and automatic scoring
- **Progress Tracking**: statistics including correct answers, wrong answers, and estimated scores

### Exam Features
- **33-Question Exams**: Full exam simulation matching standard test format
- **Automatic Scoring**: Instant feedback with score calculation (1 point for correct, -0.33 for incorrect)
- **Pass/Fail Indicators**: Visual feedback showing if the exam is passed (18+ points required)
- **Performance Metrics**: Estimated grade calculation based on current practice performance

### 🔄 Practice Mode
- **Wrong Answer Tracking**: Automatically captures answers you got wrong
- **Focused Practice**: Review only the questions you need to improve on
- **Auto-Completion**: Exits practice mode when all incorrect answers are reviewed and corrected

### 💾 Data Management
- **CSV Format Support**: Load quizzes from simple CSV files
- **Flexible Column Structure**: Supports 3 or 4 answer options per question
- **Explanation Support**: Include motivations/explanations for answers in the "motivazione" column



## Usage


### Uploading Custom Quizzes

You can upload your own quiz CSV files directly from the app without needing to place them in the project directory:

1. **Prepare Your CSV File** - Ensure it follows the format specification below
2. **Open the App** and navigate to the sidebar
3. **Click the File Uploader** under "📤 Carica Quiz Personalizzato"
4. **Select Your CSV File** from your computer
5. **Validation** - The app will automatically validate the file format
6. **Use Your Quiz** - Once uploaded successfully, your quiz appears in the topic list with a 📤 icon

Uploaded quizzes are temporary and exist only for your current session. They are not saved to the project directory.

### CSV File Format

Create quiz files as CSV with the following structure:

| Column | Description | Required |
|--------|-------------|----------|
| `domanda` | The question text | Yes |
| `opzioneA` | Answer option A | Yes |
| `opzioneB` | Answer option B | Yes |
| `opzioneC` | Answer option C | Yes |
| `opzioneD` | Answer option D | No (3 or 4 options supported) |
| `soluzione` | Correct answer (A, B, C, or D) | Yes |
| `motivazione` | Explanation for the answer | No |

**Example CSV:**
```csv
domanda,opzioneA,opzioneB,opzioneC,opzioneD,soluzione,motivazione
Cos'è il Cloud Computing?,Un tipo di computer,Distribuzione di servizi IT su Internet,Una marchio di notebook,Antivirus software,B,Il cloud computing consente l'accesso a risorse computazionali tramite Internet.
```

### Features Guide

#### 1. **Quiz Upload & Selection**
- **Upload Custom Quiz**: Use the "📤 Carica Quiz Personalizzato" section in the sidebar to upload your own CSV file
- **Auto-Detection**: The app automatically detects and lists all CSV files in the project directory
- **Topic Selection**: Use the sidebar radio buttons to select from available quiz topics
- **Uploaded Quizzes**: Uploaded quizzes appear with a 📤 icon to distinguish them from local files
- **Format Validation**: The app validates that uploaded CSV files contain all required columns before loading
- **Questions are randomly shuffled for each session**

#### 2. **Answer a Question**
- Click on any of the 3-4 answer options
- Selected answer will be highlighted in red (incorrect) or green (correct)
- Correct answer will also be shown in green
- Review the explanation if provided

#### 3. **Practice Mode**
- Click the "🔄 Pratica" button to enter practice mode
- Only questions you got wrong will appear
- Complete all wrong answers and they'll be removed from the list
- Exit practice mode once all wrong answers are mastered

#### 4. **Exam Mode**
- Enable "📝 Modalità ESAME (33 domande)" in the sidebar
- Complete exactly 33 questions
- Score is calculated in real-time
- Results show whether you passed (18+/33) or failed
- Option to restart the exam

#### 5. **Progress Tracking**
- View statistics: questions seen, correct answers, wrong answers
- See estimated grade based on current performance
- Exam mode shows live progress bar and score


## Technical Details

### Session State Management
The application uses Streamlit's session state to maintain:
- Current question and answer selections
- Quiz progress and statistics
- Wrong answers list for practice mode
- Exam mode state and scoring

### Performance Features
- Cached data loading with `@st.cache_data` for optimal performance
- Efficient DataFrame operations with pandas
- Responsive UI with CSS styling

### Error Handling
- Robust CSV loading with UTF-8 encoding handling
- Column validation to ensure required fields exist
- Graceful fallback for missing optional columns
- Demo data generation if no CSV files are found

## Keyboard Shortcuts & Tips

- **Skip Question**: Click "Salta Domanda" to move to the next question without answering
- **Practice Focus**: Use practice mode to repeatedly review challenging topics
- **Exam Simulation**: Enable exam mode to simulate real testing conditions
- **Answer Review**: Read motivations carefully to understand why answers are correct

## Customization

### Styling
Modify the CSS in the code to customize button appearance, colors, and layout:
```python
css_style = """
<style>
div.stButton > button {
    height: 85px; width: 100%; font-size: 19px;
    /* Customize here */
}
</style>
"""
```

### Exam Parameters
Change the number of exam questions by modifying:
```python
MAX_DOMANDE_ESAME = 33
```

## Troubleshooting

### CSV Upload Issues
- **"Colonne mancanti" error**: Your CSV doesn't have all required columns. Check that you have: `domanda`, `opzioneA`, `opzioneB`, `opzioneC`, `soluzione`
- **Upload doesn't appear in list**: Refresh the page or try uploading again
- **Uploaded quiz disappears**: Uploaded quizzes are session-based and reset when you refresh the page. If you want to keep a quiz, save it to the project directory

### No quizzes appear in sidebar
- Ensure CSV files are in the same directory as `app.py`
- Check file names use `.csv` extension
- Files should follow the naming convention: `Topic_Name.csv`

### CSV loading errors
- Verify CSV encoding (UTF-8 recommended)
- Check that all required columns exist
- Ensure solution column contains valid values (A, B, C, or D)

### Questions not shuffling
- The application randomly shuffles questions and answer options on each load
- If you want the same quiz again, use the browser back button or select the same topic

## Language

The application interface is in **Italian**. The CSV files can contain questions in any language.

## Dependencies

- **streamlit**: Web application framework
- **pandas**: Data manipulation and CSV handling

Install all dependencies with:
```bash
pip install -r requirements.txt
```

## Future Enhancements

Potential features for future versions:
- User authentication and progress saving
- Quiz analytics and performance reports
- Import quizzes from external sources
- Support for different answer types (multiple select, fill-in-the-blank)
- Timed questions
- Question difficulty ratings
- Leaderboard functionality

## License

This project is open source and available for educational use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify CSV file format matches the specification
3. Ensure all dependencies are properly installed
4. Clear browser cache if UI doesn't update properly