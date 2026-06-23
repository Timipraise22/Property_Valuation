from flask import Flask, request, jsonify, render_template
import pandas as pd
import joblib

# Initialize the Flask App
app = Flask(__name__)

#LOAD THE THREE PIECES OF THE BRAIN
try:
    model = joblib.load('new_lagos_property_model.pkl')
    model_cols = joblib.load('new_model_columns.pkl')
    label_encoder = joblib.load('location_encoder.pkl') 
    
    valid_locations = [loc.lower() for loc in label_encoder.classes_]
except Exception as e:
    print(f"CRITICAL ERROR LOADING FILES: {e}")
    print("Ensure 'lagos_property_model.pkl', 'model_columns.pkl', and 'location_encoder.pkl' are in this folder!")

#THE FRONT DOOR (Serves the HTML)
@app.route('/')
def home():
    return render_template('index.html')

#THE KITCHEN (Processes the Math)
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        # Grab location and clean up extra spaces
        loc = str(data.get('Location', '')).strip()
        
        #THE SECURITY CHECK
        if loc.lower() not in valid_locations:
            return jsonify({
                'success': False, 
                'error': f"Sorry, '{loc}' is not in our database. Please try a valid Lagos neighborhood."
            })
            
        #THE TRANSLATOR
        exact_loc = next(l for l in label_encoder.classes_ if l.lower() == loc.lower())
        
        # Convert text (e.g., "Lekki") to the secret number (e.g., 12)
        loc_encoded = label_encoder.transform([exact_loc])[0]
        
        # Build the exact dictionary the new AI model expects
        input_dict = {
            'Bedrooms': int(data.get('Bedrooms', 0)),
            'Bathrooms': int(data.get('Bathrooms', 0)),
            'Toilets': int(data.get('Toilets', 0)),
            'Has_Gym': int(data.get('Has_Gym', 0)),
            'Has_Pool': int(data.get('Has_Pool', 0)),
            'Has_BQ': int(data.get('Has_BQ', 0)),
            'Has_Elevator': int(data.get('Has_Elevator', 0)),
            'Location_Encoded': loc_encoded # <-- The AI only needs this one number now!
        }
            
        # Format for the AI blueprint
        input_df = pd.DataFrame([input_dict]).reindex(columns=model_cols, fill_value=0)
        
        #GET THE EXACT PREDICTION
        exact_prediction = float(model.predict(input_df)[0])
        
        #THE SCIENTIFIC PRICE RANGE
        
        mae_value = 42396964.95  
        
        lower_bound = exact_prediction - mae_value
        upper_bound = exact_prediction + mae_value
        
        # Safety check: No negative prices
        if lower_bound < 0:
            lower_bound = 0
            
        formatted_range = f"₦{lower_bound:,.2f} - ₦{upper_bound:,.2f}"
        
        #SEND BACK TO JAVASCRIPT
        return jsonify({
            'success': True, 
            'exact_price': exact_prediction,
            'price_range': formatted_range
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)