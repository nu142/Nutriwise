from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for models
llm_model = None
embedding_model = None
rag_knowledge_base = None

class NutritionInput(BaseModel):
    calories: float
    total_fat: float
    saturated_fat: float
    trans_fat: float
    cholesterol: float
    sodium: float
    total_carbs: float
    dietary_fiber: float
    total_sugars: float
    added_sugars: float
    protein: float
    vitamin_d: Optional[float] = 0
    calcium: Optional[float] = 0
    iron: Optional[float] = 0
    potassium: Optional[float] = 0
    serving_size: Optional[str] = "1 serving"
    food_name: Optional[str] = "Food Item"

class HealthGoalInput(BaseModel):
    nutrition_data: NutritionInput
    health_goal: str  # "weight_loss", "muscle_gain", "heart_health", "diabetes_management"

class DietCompatibilityInput(BaseModel):
    nutrition_data: NutritionInput
    diet_type: str  # "keto", "vegan", "paleo", "mediterranean", "low_sodium"

class ConversationalInput(BaseModel):
    nutrition_data: NutritionInput
    question: str
    context: Optional[str] = ""

# RAG Knowledge Base
NUTRITION_GUIDELINES = {
    "daily_values": {
        "calories": 2000,
        "total_fat": 65,
        "saturated_fat": 20,
        "cholesterol": 300,
        "sodium": 2300,
        "total_carbs": 300,
        "dietary_fiber": 25,
        "protein": 50,
        "added_sugars": 50
    },
    "health_goals": {
        "weight_loss": {
            "description": "Focus on low-calorie, high-fiber foods with moderate protein",
            "limits": {"calories": 1500, "total_fat": 50, "added_sugars": 25}
        },
        "muscle_gain": {
            "description": "High protein intake with balanced carbs and healthy fats",
            "targets": {"protein": 80, "calories": 2500}
        },
        "heart_health": {
            "description": "Low sodium, low saturated fat, high fiber",
            "limits": {"sodium": 1500, "saturated_fat": 13}
        },
        "diabetes_management": {
            "description": "Low added sugars, high fiber, moderate carbs",
            "limits": {"added_sugars": 25, "total_carbs": 200}
        }
    },
    "diet_compatibility": {
        "keto": {
            "description": "Very low carb, high fat, moderate protein",
            "limits": {"total_carbs": 30, "net_carbs": 20},
            "targets": {"total_fat": 70}
        },
        "vegan": {
            "description": "Plant-based diet, no animal products",
            "restrictions": ["cholesterol", "animal_fats"]
        },
        "paleo": {
            "description": "Whole foods, no processed ingredients",
            "avoid": ["added_sugars", "processed_foods"]
        },
        "mediterranean": {
            "description": "Healthy fats, moderate carbs, lean proteins",
            "encourage": ["healthy_fats", "fiber", "moderate_sodium"]
        },
        "low_sodium": {
            "description": "Reduced sodium intake for heart health",
            "limits": {"sodium": 1500}
        }
    }
}

def initialize_models():
    """Initialize LLM and embedding models"""
    global llm_model, embedding_model, rag_knowledge_base
    
    try:
        print("Starting model initialization...")
        
        # For now, use rule-based system to ensure functionality works
        # In production, you would load actual LLM models here
        llm_model = "rule_based"  # Placeholder
        embedding_model = "rule_based"  # Placeholder
        
        # Create knowledge base embeddings
        print("Creating RAG knowledge base...")
        rag_knowledge_base = create_rag_knowledge_base()
        
        print("Models initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing models: {e}")
        # Fallback to a simple rule-based system if models fail
        llm_model = None
        embedding_model = None

def create_rag_knowledge_base():
    """Create embeddings for nutrition guidelines"""
    knowledge_texts = []
    
    # Daily values information
    for nutrient, value in NUTRITION_GUIDELINES["daily_values"].items():
        knowledge_texts.append(f"The daily value for {nutrient} is {value}")
    
    # Health goals information
    for goal, info in NUTRITION_GUIDELINES["health_goals"].items():
        knowledge_texts.append(f"For {goal}: {info['description']}")
    
    # Diet compatibility information
    for diet, info in NUTRITION_GUIDELINES["diet_compatibility"].items():
        knowledge_texts.append(f"For {diet} diet: {info['description']}")
    
    # For now, return simple text-based knowledge base
    return {"texts": knowledge_texts, "embeddings": None}

def get_relevant_knowledge(query: str, top_k: int = 3):
    """Retrieve relevant knowledge using simple text matching"""
    if not rag_knowledge_base:
        return []
    
    # Simple keyword matching for now
    relevant_texts = []
    query_lower = query.lower()
    
    for text in rag_knowledge_base["texts"]:
        # Simple scoring based on keyword matches
        if any(word in text.lower() for word in query_lower.split()):
            relevant_texts.append(text)
    
    return relevant_texts[:top_k]

def generate_llm_response(prompt: str, max_length: int = 200):
    """Generate response using rule-based system"""
    # For now, use enhanced rule-based responses
    return generate_rule_based_response(prompt)

def generate_rule_based_response(prompt: str):
    """Enhanced rule-based response generation"""
    prompt_lower = prompt.lower()
    
    # Functionality 1: Simplification
    if "simplify" in prompt_lower or "explain" in prompt_lower:
        if "calories" in prompt_lower:
            return "This nutrition label shows the caloric content and essential nutrients per serving. The calories indicate energy content, while other nutrients like protein, fats, and carbs provide building blocks for your body."
        return "This nutrition label provides key information about the nutritional content of this food item, including macronutrients and micronutrients per serving."
    
    # Functionality 2: Health goals
    elif "health goal" in prompt_lower or "weight loss" in prompt_lower:
        if "weight loss" in prompt_lower:
            return "For weight loss, focus on foods with moderate calories, high protein, and low added sugars. This food's nutritional profile should be evaluated against your daily calorie goals."
        elif "muscle gain" in prompt_lower:
            return "For muscle gain, prioritize foods high in protein and adequate calories. Look for lean protein sources and balanced macronutrients."
        elif "heart health" in prompt_lower:
            return "For heart health, choose foods low in sodium and saturated fats, with good fiber content. Monitor cholesterol intake."
        elif "diabetes" in prompt_lower:
            return "For diabetes management, focus on foods with low added sugars, high fiber, and complex carbohydrates to help manage blood sugar levels."
        return "This food's suitability for your health goals depends on your specific nutritional needs and daily targets."
    
    # Functionality 3: Diet compatibility
    elif "diet" in prompt_lower or "keto" in prompt_lower or "vegan" in prompt_lower:
        if "keto" in prompt_lower:
            return "For keto diet compatibility, check that this food is very low in carbohydrates (under 10g net carbs) and high in healthy fats."
        elif "vegan" in prompt_lower:
            return "For vegan diet compatibility, ensure this food contains no animal products, including no cholesterol and no animal-derived ingredients."
        elif "paleo" in prompt_lower:
            return "For paleo diet compatibility, this food should be minimally processed and contain no grains, legumes, or added sugars."
        return "Diet compatibility depends on the specific restrictions and guidelines of your chosen dietary approach."
    
    # Functionality 4: Conversational
    elif "?" in prompt_lower or "how" in prompt_lower or "what" in prompt_lower:
        if "sodium" in prompt_lower:
            return "Sodium content affects blood pressure and heart health. The recommended daily limit is 2,300mg for most adults."
        elif "sugar" in prompt_lower:
            return "Added sugars provide calories without essential nutrients. The daily limit is around 50g for most adults."
        elif "protein" in prompt_lower:
            return "Protein is essential for muscle maintenance and growth. Most adults need about 0.8g per kg of body weight daily."
        elif "fat" in prompt_lower:
            return "Fats provide essential fatty acids and fat-soluble vitamins. Focus on unsaturated fats and limit saturated fats."
        return "I can help you understand any aspect of this nutrition information. Feel free to ask about specific nutrients or health implications."
    
    # Functionality 5: Warnings
    elif "warning" in prompt_lower or "alert" in prompt_lower:
        return "Based on the nutrition analysis, I can identify potential health concerns and suggest healthier alternatives to support your wellness goals."
    
    else:
        return "I can help you understand this nutrition information, check diet compatibility, assess health goals, and provide personalized insights. What would you like to know?"

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    initialize_models()

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "models_loaded": llm_model is not None}

@app.post("/api/nutrition/simplify")
async def simplify_nutrition_label(nutrition: NutritionInput):
    """Functionality 1: Nutritional Label Simplification"""
    try:
        # Get relevant knowledge
        query = f"explain nutrition label with {nutrition.calories} calories"
        relevant_knowledge = get_relevant_knowledge(query)
        
        # Create prompt
        prompt = f"""
        Simplify this nutrition label for easy understanding:
        
        Food: {nutrition.food_name}
        Serving Size: {nutrition.serving_size}
        Calories: {nutrition.calories}
        Total Fat: {nutrition.total_fat}g
        Saturated Fat: {nutrition.saturated_fat}g
        Cholesterol: {nutrition.cholesterol}mg
        Sodium: {nutrition.sodium}mg
        Total Carbohydrates: {nutrition.total_carbs}g
        Dietary Fiber: {nutrition.dietary_fiber}g
        Total Sugars: {nutrition.total_sugars}g
        Added Sugars: {nutrition.added_sugars}g
        Protein: {nutrition.protein}g
        
        Context: {' '.join(relevant_knowledge)}
        
        Provide a simple, friendly explanation of what these numbers mean:
        """
        
        response = generate_llm_response(prompt)
        
        # Calculate daily value percentages
        daily_values = NUTRITION_GUIDELINES["daily_values"]
        percentages = {}
        for nutrient in ["calories", "total_fat", "saturated_fat", "cholesterol", "sodium", "total_carbs", "dietary_fiber", "protein"]:
            if hasattr(nutrition, nutrient) and nutrient in daily_values:
                value = getattr(nutrition, nutrient)
                percentages[nutrient] = round((value / daily_values[nutrient]) * 100, 1)
        
        return {
            "simplified_explanation": response,
            "daily_value_percentages": percentages,
            "key_insights": [
                f"This serving contains {nutrition.calories} calories",
                f"Provides {nutrition.protein}g of protein",
                f"Contains {nutrition.total_fat}g of fat",
                f"Has {nutrition.added_sugars}g of added sugars"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing nutrition label: {str(e)}")

@app.post("/api/nutrition/health-goal")
async def check_health_goal_suitability(goal_input: HealthGoalInput):
    """Functionality 2: Health Goal Suitability"""
    try:
        nutrition = goal_input.nutrition_data
        health_goal = goal_input.health_goal
        
        # Get relevant knowledge
        query = f"health goal {health_goal} nutrition suitability"
        relevant_knowledge = get_relevant_knowledge(query)
        
        # Get goal-specific guidelines
        goal_info = NUTRITION_GUIDELINES["health_goals"].get(health_goal, {})
        
        # Create prompt
        prompt = f"""
        Analyze if this food is suitable for the health goal: {health_goal}
        
        Nutrition Information:
        Calories: {nutrition.calories}
        Total Fat: {nutrition.total_fat}g
        Saturated Fat: {nutrition.saturated_fat}g
        Sodium: {nutrition.sodium}mg
        Added Sugars: {nutrition.added_sugars}g
        Protein: {nutrition.protein}g
        Fiber: {nutrition.dietary_fiber}g
        
        Health Goal: {health_goal}
        Goal Description: {goal_info.get('description', '')}
        
        Context: {' '.join(relevant_knowledge)}
        
        Provide a clear verdict on whether this food aligns with the health goal:
        """
        
        response = generate_llm_response(prompt)
        
        # Rule-based evaluation
        suitability_score = calculate_health_goal_score(nutrition, health_goal)
        
        return {
            "health_goal": health_goal,
            "suitability_verdict": response,
            "suitability_score": suitability_score,
            "recommendation": get_health_goal_recommendation(suitability_score),
            "goal_info": goal_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing health goal suitability: {str(e)}")

@app.post("/api/nutrition/diet-compatibility")
async def check_diet_compatibility(diet_input: DietCompatibilityInput):
    """Functionality 3: Diet Compatibility Checker"""
    try:
        nutrition = diet_input.nutrition_data
        diet_type = diet_input.diet_type
        
        # Get relevant knowledge
        query = f"diet compatibility {diet_type} nutrition"
        relevant_knowledge = get_relevant_knowledge(query)
        
        # Get diet-specific guidelines
        diet_info = NUTRITION_GUIDELINES["diet_compatibility"].get(diet_type, {})
        
        # Create prompt
        prompt = f"""
        Check if this food is compatible with the {diet_type} diet:
        
        Nutrition Information:
        Calories: {nutrition.calories}
        Total Fat: {nutrition.total_fat}g
        Total Carbs: {nutrition.total_carbs}g
        Dietary Fiber: {nutrition.dietary_fiber}g
        Protein: {nutrition.protein}g
        Sodium: {nutrition.sodium}mg
        Added Sugars: {nutrition.added_sugars}g
        
        Diet Type: {diet_type}
        Diet Description: {diet_info.get('description', '')}
        
        Context: {' '.join(relevant_knowledge)}
        
        Explain the compatibility with reasoning:
        """
        
        response = generate_llm_response(prompt)
        
        # Rule-based compatibility check
        compatibility_score = calculate_diet_compatibility_score(nutrition, diet_type)
        
        return {
            "diet_type": diet_type,
            "compatibility_explanation": response,
            "compatibility_score": compatibility_score,
            "is_compatible": compatibility_score >= 70,
            "diet_info": diet_info,
            "specific_concerns": get_diet_specific_concerns(nutrition, diet_type)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking diet compatibility: {str(e)}")

@app.post("/api/nutrition/chat")
async def conversational_assistant(chat_input: ConversationalInput):
    """Functionality 4: Conversational Query Assistant"""
    try:
        nutrition = chat_input.nutrition_data
        question = chat_input.question
        context = chat_input.context
        
        # Get relevant knowledge
        relevant_knowledge = get_relevant_knowledge(question)
        
        # Create prompt
        prompt = f"""
        Answer this question about the nutrition information:
        
        Question: {question}
        
        Nutrition Information:
        Food: {nutrition.food_name}
        Calories: {nutrition.calories}
        Total Fat: {nutrition.total_fat}g
        Saturated Fat: {nutrition.saturated_fat}g
        Cholesterol: {nutrition.cholesterol}mg
        Sodium: {nutrition.sodium}mg
        Total Carbs: {nutrition.total_carbs}g
        Dietary Fiber: {nutrition.dietary_fiber}g
        Total Sugars: {nutrition.total_sugars}g
        Added Sugars: {nutrition.added_sugars}g
        Protein: {nutrition.protein}g
        
        Context: {context}
        Knowledge: {' '.join(relevant_knowledge)}
        
        Provide a helpful, conversational answer:
        """
        
        response = generate_llm_response(prompt)
        
        return {
            "question": question,
            "answer": response,
            "relevant_facts": relevant_knowledge[:2],
            "follow_up_suggestions": [
                "How does this compare to daily recommended values?",
                "What are the health implications of these nutrients?",
                "Are there any concerns with this food item?"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in conversational assistant: {str(e)}")

@app.post("/api/nutrition/warnings")
async def generate_warnings_and_suggestions(nutrition: NutritionInput):
    """Functionality 5: Smart Warnings and Suggestions"""
    try:
        # Get relevant knowledge
        query = f"nutrition warnings health alerts {nutrition.food_name}"
        relevant_knowledge = get_relevant_knowledge(query)
        
        # Create prompt
        prompt = f"""
        Analyze this nutrition label for health warnings and provide suggestions:
        
        Food: {nutrition.food_name}
        Calories: {nutrition.calories}
        Total Fat: {nutrition.total_fat}g
        Saturated Fat: {nutrition.saturated_fat}g
        Sodium: {nutrition.sodium}mg
        Added Sugars: {nutrition.added_sugars}g
        Protein: {nutrition.protein}g
        
        Context: {' '.join(relevant_knowledge)}
        
        Provide health warnings and alternative suggestions:
        """
        
        response = generate_llm_response(prompt)
        
        # Rule-based warnings
        warnings = generate_health_warnings(nutrition)
        suggestions = generate_healthy_alternatives(nutrition)
        
        return {
            "ai_analysis": response,
            "health_warnings": warnings,
            "alternative_suggestions": suggestions,
            "overall_health_score": calculate_overall_health_score(nutrition),
            "improvement_tips": get_improvement_tips(nutrition)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating warnings: {str(e)}")

# Helper functions
def calculate_health_goal_score(nutrition: NutritionInput, health_goal: str) -> int:
    """Calculate suitability score for health goals"""
    score = 50  # Base score
    
    if health_goal == "weight_loss":
        if nutrition.calories < 300: score += 20
        if nutrition.total_fat < 10: score += 15
        if nutrition.added_sugars < 5: score += 15
    elif health_goal == "muscle_gain":
        if nutrition.protein > 15: score += 25
        if nutrition.calories > 200: score += 15
    elif health_goal == "heart_health":
        if nutrition.sodium < 400: score += 20
        if nutrition.saturated_fat < 3: score += 20
        if nutrition.dietary_fiber > 5: score += 10
    elif health_goal == "diabetes_management":
        if nutrition.added_sugars < 3: score += 25
        if nutrition.dietary_fiber > 5: score += 15
    
    return min(100, max(0, score))

def calculate_diet_compatibility_score(nutrition: NutritionInput, diet_type: str) -> int:
    """Calculate compatibility score for diets"""
    score = 50  # Base score
    
    if diet_type == "keto":
        net_carbs = nutrition.total_carbs - nutrition.dietary_fiber
        if net_carbs < 5: score += 30
        if nutrition.total_fat > 15: score += 20
    elif diet_type == "low_sodium":
        if nutrition.sodium < 300: score += 30
        if nutrition.sodium < 150: score += 20
    elif diet_type == "vegan":
        if nutrition.cholesterol == 0: score += 25
        score += 25  # Assume plant-based if no cholesterol
    
    return min(100, max(0, score))

def calculate_overall_health_score(nutrition: NutritionInput) -> int:
    """Calculate overall health score"""
    score = 50
    daily_values = NUTRITION_GUIDELINES["daily_values"]
    
    # Positive factors
    if nutrition.dietary_fiber > 5: score += 15
    if nutrition.protein > 10: score += 10
    
    # Negative factors
    if nutrition.added_sugars > daily_values["added_sugars"] * 0.2: score -= 15
    if nutrition.sodium > daily_values["sodium"] * 0.3: score -= 15
    if nutrition.saturated_fat > daily_values["saturated_fat"] * 0.3: score -= 10
    
    return min(100, max(0, score))

def get_health_goal_recommendation(score: int) -> str:
    """Get recommendation based on health goal score"""
    if score >= 80: return "Excellent choice for your health goal!"
    elif score >= 60: return "Good option with minor considerations"
    elif score >= 40: return "Okay choice, but could be better"
    else: return "Consider healthier alternatives"

def get_diet_specific_concerns(nutrition: NutritionInput, diet_type: str) -> List[str]:
    """Get specific concerns for diet types"""
    concerns = []
    
    if diet_type == "keto":
        net_carbs = nutrition.total_carbs - nutrition.dietary_fiber
        if net_carbs > 10: concerns.append(f"High net carbs: {net_carbs}g")
    elif diet_type == "low_sodium":
        if nutrition.sodium > 400: concerns.append(f"High sodium: {nutrition.sodium}mg")
    elif diet_type == "vegan":
        if nutrition.cholesterol > 0: concerns.append("Contains cholesterol (not vegan)")
    
    return concerns

def generate_health_warnings(nutrition: NutritionInput) -> List[str]:
    """Generate health warnings based on nutrition values"""
    warnings = []
    daily_values = NUTRITION_GUIDELINES["daily_values"]
    
    if nutrition.sodium > daily_values["sodium"] * 0.4:
        warnings.append("⚠️ High sodium content - may affect blood pressure")
    if nutrition.added_sugars > daily_values["added_sugars"] * 0.3:
        warnings.append("⚠️ High added sugars - may cause blood sugar spikes")
    if nutrition.saturated_fat > daily_values["saturated_fat"] * 0.4:
        warnings.append("⚠️ High saturated fat - may impact heart health")
    if nutrition.calories > 500:
        warnings.append("⚠️ High calorie content - consume in moderation")
    
    return warnings

def generate_healthy_alternatives(nutrition: NutritionInput) -> List[str]:
    """Generate healthy alternative suggestions"""
    suggestions = []
    
    if nutrition.added_sugars > 10:
        suggestions.append("🍎 Try fresh fruits instead of processed sweets")
    if nutrition.sodium > 600:
        suggestions.append("🥗 Look for low-sodium versions or fresh alternatives")
    if nutrition.saturated_fat > 10:
        suggestions.append("🥑 Consider foods with healthy fats like avocados or nuts")
    if nutrition.dietary_fiber < 3:
        suggestions.append("🌾 Add more fiber-rich foods like whole grains")
    
    return suggestions

def get_improvement_tips(nutrition: NutritionInput) -> List[str]:
    """Get tips for improving nutrition"""
    tips = []
    
    if nutrition.protein < 10:
        tips.append("💪 Add more protein sources to your meal")
    if nutrition.dietary_fiber < 5:
        tips.append("🌿 Include more vegetables and whole grains")
    if nutrition.added_sugars > 15:
        tips.append("🍯 Try natural sweeteners instead of added sugars")
    
    return tips

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)