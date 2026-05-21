import os
from dotenv import load_dotenv

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

try:
    from .predictor import predict
    from .gradcam import generate_gradcam
    from .chatbot import ask_chatbot
except ImportError:
    from predictor import predict
    from gradcam import generate_gradcam
    from chatbot import ask_chatbot

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Breed Information Database ----
BREED_INFO = {
    "Chihuahua":              {"origin": "Mexico",        "size": "Toy",    "lifespan": "12–20 yrs", "temperament": "Charming, Graceful, Sassy"},
    "Japanese Spaniel":       {"origin": "Japan",         "size": "Small",  "lifespan": "10–12 yrs", "temperament": "Loyal, Intelligent, Alert"},
    "Maltese Dog":            {"origin": "Malta",         "size": "Toy",    "lifespan": "12–15 yrs", "temperament": "Gentle, Playful, Fearless"},
    "Pekinese":               {"origin": "China",         "size": "Small",  "lifespan": "12–15 yrs", "temperament": "Affectionate, Loyal, Regal"},
    "Shih Tzu":               {"origin": "China",         "size": "Small",  "lifespan": "10–16 yrs", "temperament": "Affectionate, Playful, Outgoing"},
    "Blenheim Spaniel":       {"origin": "UK",            "size": "Small",  "lifespan": "12–15 yrs", "temperament": "Gentle, Graceful, Fearless"},
    "Papillon":               {"origin": "France",        "size": "Toy",    "lifespan": "13–15 yrs", "temperament": "Friendly, Energetic, Alert"},
    "Toy Terrier":            {"origin": "UK",            "size": "Toy",    "lifespan": "12–14 yrs", "temperament": "Spirited, Clever, Loving"},
    "Rhodesian Ridgeback":    {"origin": "South Africa",  "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Loyal, Strong-Willed, Dignified"},
    "Afghan Hound":           {"origin": "Afghanistan",   "size": "Large",  "lifespan": "12–14 yrs", "temperament": "Aloof, Clownish, Dignified"},
    "Basset":                 {"origin": "France",        "size": "Medium", "lifespan": "10–12 yrs", "temperament": "Tenacious, Friendly, Gentle"},
    "Beagle":                 {"origin": "UK",            "size": "Medium", "lifespan": "12–15 yrs", "temperament": "Curious, Merry, Friendly"},
    "Bloodhound":             {"origin": "Belgium",       "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Stubborn, Affectionate, Gentle"},
    "Bluetick":               {"origin": "USA",           "size": "Medium", "lifespan": "11–12 yrs", "temperament": "Intelligent, Active, Friendly"},
    "Black And Tan Coonhound":{"origin": "USA",           "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Easygoing, Calm, Trusting"},
    "Walker Hound":           {"origin": "USA",           "size": "Medium", "lifespan": "12–13 yrs", "temperament": "Smart, Brave, Courteous"},
    "English Foxhound":       {"origin": "UK",            "size": "Medium", "lifespan": "10–13 yrs", "temperament": "Gentle, Sociable, Active"},
    "Redbone":                {"origin": "USA",           "size": "Medium", "lifespan": "11–12 yrs", "temperament": "Eager, Trainable, Affectionate"},
    "Borzoi":                 {"origin": "Russia",        "size": "Large",  "lifespan": "9–14 yrs",  "temperament": "Respectful, Athletic, Intelligent"},
    "Irish Wolfhound":        {"origin": "Ireland",       "size": "Giant",  "lifespan": "6–10 yrs",  "temperament": "Loyal, Dignified, Generous"},
    "Italian Greyhound":      {"origin": "Italy",         "size": "Small",  "lifespan": "14–15 yrs", "temperament": "Playful, Athletic, Gentle"},
    "Whippet":                {"origin": "UK",            "size": "Medium", "lifespan": "12–15 yrs", "temperament": "Affectionate, Lively, Gentle"},
    "Ibizan Hound":           {"origin": "Spain",         "size": "Medium", "lifespan": "12–14 yrs", "temperament": "Engaging, Stubborn, Active"},
    "Norwegian Elkhound":     {"origin": "Norway",        "size": "Medium", "lifespan": "12–15 yrs", "temperament": "Bold, Energetic, Playful"},
    "Otterhound":             {"origin": "UK",            "size": "Large",  "lifespan": "10–13 yrs", "temperament": "Boisterous, Amiable, Even-Tempered"},
    "Saluki":                 {"origin": "Middle East",   "size": "Large",  "lifespan": "12–14 yrs", "temperament": "Reserved, Aloof, Gentle"},
    "Scottish Deerhound":     {"origin": "Scotland",      "size": "Large",  "lifespan": "8–11 yrs",  "temperament": "Docile, Friendly, Dignified"},
    "Weimaraner":             {"origin": "Germany",       "size": "Large",  "lifespan": "11–14 yrs", "temperament": "Friendly, Fearless, Alert"},
    "Staffordshire Bullterrier": {"origin": "UK",         "size": "Medium", "lifespan": "12–14 yrs", "temperament": "Loyal, Fearless, Reliable"},
    "American Staffordshire Terrier": {"origin": "USA",   "size": "Medium", "lifespan": "12–16 yrs", "temperament": "Confident, Smart, Loyal"},
    "Bedlington Terrier":     {"origin": "UK",            "size": "Small",  "lifespan": "14–16 yrs", "temperament": "Loyal, Spirited, Intelligent"},
    "Border Terrier":         {"origin": "UK",            "size": "Small",  "lifespan": "12–15 yrs", "temperament": "Affectionate, Happy, Even-Tempered"},
    "Kerry Blue Terrier":     {"origin": "Ireland",       "size": "Medium", "lifespan": "13–15 yrs", "temperament": "Loyal, Alert, Adaptable"},
    "Irish Terrier":          {"origin": "Ireland",       "size": "Medium", "lifespan": "13–15 yrs", "temperament": "Lively, Protective, Dominant"},
    "Norfolk Terrier":        {"origin": "UK",            "size": "Small",  "lifespan": "12–15 yrs", "temperament": "Fearless, Lovable, Spirited"},
    "Norwich Terrier":        {"origin": "UK",            "size": "Small",  "lifespan": "12–15 yrs", "temperament": "Fearless, Lovable, Loyal"},
    "Yorkshire Terrier":      {"origin": "UK",            "size": "Toy",    "lifespan": "13–16 yrs", "temperament": "Bold, Independent, Confident"},
    "Wire-Haired Fox Terrier":{"origin": "UK",            "size": "Small",  "lifespan": "13–15 yrs", "temperament": "Fearless, Alert, Confident"},
    "Lakeland Terrier":       {"origin": "UK",            "size": "Small",  "lifespan": "12–16 yrs", "temperament": "Bold, Friendly, Confident"},
    "Sealyham Terrier":       {"origin": "Wales",         "size": "Small",  "lifespan": "12–14 yrs", "temperament": "Calm, Alert, Outgoing"},
    "Airedale":               {"origin": "UK",            "size": "Large",  "lifespan": "11–14 yrs", "temperament": "Outgoing, Friendly, Confident"},
    "Cairn":                  {"origin": "Scotland",      "size": "Small",  "lifespan": "13–15 yrs", "temperament": "Hardy, Fearless, Assertive"},
    "Australian Terrier":     {"origin": "Australia",     "size": "Small",  "lifespan": "11–15 yrs", "temperament": "Spirited, Alert, Loyal"},
    "Dandie Dinmont":         {"origin": "UK",            "size": "Small",  "lifespan": "12–15 yrs", "temperament": "Independent, Determined, Reserved"},
    "Boston Bull":            {"origin": "USA",           "size": "Small",  "lifespan": "13–15 yrs", "temperament": "Friendly, Bright, Amusing"},
    "Miniature Schnauzer":    {"origin": "Germany",       "size": "Small",  "lifespan": "12–15 yrs", "temperament": "Friendly, Obedient, Intelligent"},
    "Giant Schnauzer":        {"origin": "Germany",       "size": "Large",  "lifespan": "12–15 yrs", "temperament": "Loyal, Intelligent, Powerful"},
    "Standard Schnauzer":     {"origin": "Germany",       "size": "Medium", "lifespan": "13–16 yrs", "temperament": "Trainable, Devoted, Lively"},
    "Scotch Terrier":         {"origin": "Scotland",      "size": "Small",  "lifespan": "11–13 yrs", "temperament": "Feisty, Independent, Loyal"},
    "Tibetan Terrier":        {"origin": "Tibet",         "size": "Medium", "lifespan": "12–15 yrs", "temperament": "Gentle, Loyal, Reserved"},
    "Silky Terrier":          {"origin": "Australia",     "size": "Toy",    "lifespan": "13–15 yrs", "temperament": "Friendly, Joyful, Alert"},
    "Soft-Coated Wheaten Terrier": {"origin": "Ireland",  "size": "Medium", "lifespan": "12–15 yrs", "temperament": "Playful, Energetic, Spirited"},
    "West Highland White Terrier": {"origin": "Scotland", "size": "Small",  "lifespan": "13–15 yrs", "temperament": "Hardy, Independent, Alert"},
    "Lhasa":                  {"origin": "Tibet",         "size": "Small",  "lifespan": "12–15 yrs", "temperament": "Assertive, Playful, Devoted"},
    "Flat-Coated Retriever":  {"origin": "UK",            "size": "Large",  "lifespan": "8–10 yrs",  "temperament": "Devoted, Confident, Optimistic"},
    "Curly-Coated Retriever": {"origin": "UK",            "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Confident, Trainable, Proud"},
    "Golden Retriever":       {"origin": "Scotland",      "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Friendly, Reliable, Trustworthy"},
    "Labrador Retriever":     {"origin": "Canada",        "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Kind, Outgoing, Agile"},
    "Chesapeake Bay Retriever":{"origin": "USA",          "size": "Large",  "lifespan": "10–13 yrs", "temperament": "Affectionate, Intelligent, Quiet"},
    "German Short-Haired Pointer": {"origin": "Germany",  "size": "Large",  "lifespan": "12–14 yrs", "temperament": "Intelligent, Bold, Boisterous"},
    "Vizsla":                 {"origin": "Hungary",       "size": "Medium", "lifespan": "12–15 yrs", "temperament": "Energetic, Loyal, Gentle"},
    "English Setter":         {"origin": "UK",            "size": "Large",  "lifespan": "11–15 yrs", "temperament": "Gentle, Placid, Friendly"},
    "Irish Setter":           {"origin": "Ireland",       "size": "Large",  "lifespan": "12–15 yrs", "temperament": "Playful, Energetic, Companionable"},
    "Gordon Setter":          {"origin": "Scotland",      "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Alert, Loyal, Confident"},
    "Brittany Spaniel":       {"origin": "France",        "size": "Medium", "lifespan": "12–14 yrs", "temperament": "Adaptable, Agile, Intelligent"},
    "Clumber":                {"origin": "UK",            "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Loyal, Calm, Dignified"},
    "English Springer":       {"origin": "UK",            "size": "Medium", "lifespan": "12–14 yrs", "temperament": "Friendly, Playful, Obedient"},
    "Welsh Springer Spaniel": {"origin": "Wales",         "size": "Medium", "lifespan": "12–15 yrs", "temperament": "Active, Loyal, Reserved"},
    "Cocker Spaniel":         {"origin": "USA",           "size": "Medium", "lifespan": "12–15 yrs", "temperament": "Gentle, Smart, Happy"},
    "Sussex Spaniel":         {"origin": "UK",            "size": "Medium", "lifespan": "11–13 yrs", "temperament": "Friendly, Calm, Loyal"},
    "Irish Water Spaniel":    {"origin": "Ireland",       "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Playful, Hardworking, Loyal"},
    "Kuvasz":                 {"origin": "Hungary",       "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Loyal, Patient, Protective"},
    "Schipperke":             {"origin": "Belgium",       "size": "Small",  "lifespan": "13–15 yrs", "temperament": "Curious, Energetic, Confident"},
    "Groenendael":            {"origin": "Belgium",       "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Alert, Loyal, Intelligent"},
    "Malinois":               {"origin": "Belgium",       "size": "Large",  "lifespan": "14–16 yrs", "temperament": "Confident, Smart, Hardworking"},
    "Briard":                 {"origin": "France",        "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Loyal, Fearless, Intelligent"},
    "Kelpie":                 {"origin": "Australia",     "size": "Medium", "lifespan": "10–15 yrs", "temperament": "Energetic, Loyal, Alert"},
    "Komondor":               {"origin": "Hungary",       "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Steady, Fearless, Loyal"},
    "Old English Sheepdog":   {"origin": "UK",            "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Playful, Adaptable, Bubbly"},
    "Shetland Sheepdog":      {"origin": "Scotland",      "size": "Small",  "lifespan": "12–13 yrs", "temperament": "Loyal, Trainable, Energetic"},
    "Collie":                 {"origin": "Scotland",      "size": "Large",  "lifespan": "12–14 yrs", "temperament": "Loyal, Graceful, Devoted"},
    "Border Collie":          {"origin": "UK",            "size": "Medium", "lifespan": "12–15 yrs", "temperament": "Energetic, Responsive, Alert"},
    "Bouvier Des Flandres":   {"origin": "Belgium",       "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Rational, Loyal, Protective"},
    "Rottweiler":             {"origin": "Germany",       "size": "Large",  "lifespan": "8–10 yrs",  "temperament": "Loyal, Loving, Confident"},
    "German Shepherd":        {"origin": "Germany",       "size": "Large",  "lifespan": "9–13 yrs",  "temperament": "Loyal, Courageous, Confident"},
    "Doberman":               {"origin": "Germany",       "size": "Large",  "lifespan": "10–13 yrs", "temperament": "Loyal, Fearless, Alert"},
    "Miniature Pinscher":     {"origin": "Germany",       "size": "Toy",    "lifespan": "14–15 yrs", "temperament": "Clever, Friendly, Energetic"},
    "Greater Swiss Mountain Dog": {"origin": "Switzerland","size": "Large", "lifespan": "8–11 yrs",  "temperament": "Faithful, Alert, Enthusiastic"},
    "Bernese Mountain Dog":   {"origin": "Switzerland",   "size": "Large",  "lifespan": "7–10 yrs",  "temperament": "Affectionate, Loyal, Faithful"},
    "Appenzeller":            {"origin": "Switzerland",   "size": "Medium", "lifespan": "12–14 yrs", "temperament": "Energetic, Lively, Self-Assured"},
    "Entlebucher":            {"origin": "Switzerland",   "size": "Medium", "lifespan": "11–13 yrs", "temperament": "Loyal, Enthusiastic, Agile"},
    "Boxer":                  {"origin": "Germany",       "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Playful, Devoted, Loyal"},
    "Bull Mastiff":           {"origin": "UK",            "size": "Large",  "lifespan": "8–10 yrs",  "temperament": "Loyal, Devoted, Alert"},
    "Tibetan Mastiff":        {"origin": "Tibet",         "size": "Large",  "lifespan": "12–15 yrs", "temperament": "Aloof, Loyal, Stubborn"},
    "French Bulldog":         {"origin": "France",        "size": "Small",  "lifespan": "10–12 yrs", "temperament": "Playful, Affectionate, Easygoing"},
    "Great Dane":             {"origin": "Germany",       "size": "Giant",  "lifespan": "8–10 yrs",  "temperament": "Friendly, Patient, Dependable"},
    "Saint Bernard":          {"origin": "Switzerland",   "size": "Giant",  "lifespan": "8–10 yrs",  "temperament": "Gentle, Friendly, Watchful"},
    "Eskimo Dog":             {"origin": "Canada",        "size": "Large",  "lifespan": "12–15 yrs", "temperament": "Alert, Friendly, Gentle"},
    "Malamute":               {"origin": "USA",           "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Playful, Devoted, Friendly"},
    "Siberian Husky":         {"origin": "Russia",        "size": "Medium", "lifespan": "12–14 yrs", "temperament": "Outgoing, Mischievous, Loyal"},
    "Affenpinscher":          {"origin": "Germany",       "size": "Toy",    "lifespan": "12–15 yrs", "temperament": "Curious, Playful, Adventurous"},
    "Basenji":                {"origin": "Congo",         "size": "Small",  "lifespan": "13–14 yrs", "temperament": "Playful, Energetic, Alert"},
    "Pug":                    {"origin": "China",         "size": "Toy",    "lifespan": "12–15 yrs", "temperament": "Charming, Mischievous, Loving"},
    "Leonberg":               {"origin": "Germany",       "size": "Giant",  "lifespan": "8–9 yrs",   "temperament": "Gentle, Loyal, Fearless"},
    "Newfoundland":           {"origin": "Canada",        "size": "Giant",  "lifespan": "8–10 yrs",  "temperament": "Sweet, Patient, Devoted"},
    "Great Pyrenees":         {"origin": "France",        "size": "Large",  "lifespan": "10–12 yrs", "temperament": "Patient, Calm, Smart"},
    "Samoyed":                {"origin": "Russia",        "size": "Medium", "lifespan": "12–14 yrs", "temperament": "Lively, Playful, Adaptable"},
    "Pomeranian":             {"origin": "Germany",       "size": "Toy",    "lifespan": "12–16 yrs", "temperament": "Playful, Friendly, Bold"},
    "Chow":                   {"origin": "China",         "size": "Medium", "lifespan": "9–15 yrs",  "temperament": "Loyal, Independent, Quiet"},
    "Keeshond":               {"origin": "Netherlands",   "size": "Medium", "lifespan": "12–15 yrs", "temperament": "Outgoing, Agile, Obedient"},
    "Brabancon Griffon":      {"origin": "Belgium",       "size": "Toy",    "lifespan": "12–15 yrs", "temperament": "Curious, Alert, Sensitive"},
    "Pembroke":               {"origin": "Wales",         "size": "Small",  "lifespan": "12–15 yrs", "temperament": "Playful, Tenacious, Friendly"},
    "Cardigan":               {"origin": "Wales",         "size": "Small",  "lifespan": "12–15 yrs", "temperament": "Loyal, Affectionate, Alert"},
    "Toy Poodle":             {"origin": "France",        "size": "Toy",    "lifespan": "14–18 yrs", "temperament": "Intelligent, Active, Alert"},
    "Miniature Poodle":       {"origin": "France",        "size": "Small",  "lifespan": "14–18 yrs", "temperament": "Intelligent, Active, Trainable"},
    "Standard Poodle":        {"origin": "France",        "size": "Large",  "lifespan": "12–15 yrs", "temperament": "Intelligent, Active, Instinctual"},
    "Mexican Hairless":       {"origin": "Mexico",        "size": "Medium", "lifespan": "13–18 yrs", "temperament": "Loyal, Alert, Calm"},
    "Dingo":                  {"origin": "Australia",     "size": "Medium", "lifespan": "5–10 yrs",  "temperament": "Alert, Loyal, Adaptable"},
    "Dhole":                  {"origin": "Asia",          "size": "Medium", "lifespan": "10–13 yrs", "temperament": "Social, Energetic, Alert"},
    "African Hunting Dog":    {"origin": "Africa",        "size": "Medium", "lifespan": "10–12 yrs", "temperament": "Social, Energetic, Loyal"},
}

def get_breed_info(breed_name: str):
    # Try exact match first
    if breed_name in BREED_INFO:
        return BREED_INFO[breed_name]
    # Try partial match
    for key in BREED_INFO:
        if key.lower() in breed_name.lower() or breed_name.lower() in key.lower():
            return BREED_INFO[key]
    # Default if not found
    return {
        "origin"      : "Unknown",
        "size"        : "Unknown",
        "lifespan"    : "Unknown",
        "temperament" : "Loyal, Friendly"
    }

# ---- Routes ----
@app.get("/")
def home():
    return {"status": "Pawdentify API is running! 🐾"}

@app.post("/predict")
async def predict_breed(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        results = predict(image_bytes)
        top_breed = results[0]["breed"]
        breed_info = get_breed_info(top_breed)
        return {
            "top_breed": top_breed,
            "confidence": results[0]["confidence"],
            "breed_info": breed_info,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc

@app.post("/gradcam")
async def get_gradcam(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        img_bytes, breed = generate_gradcam(image_bytes)
        return StreamingResponse(img_bytes, media_type="image/png")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"GradCAM failed: {exc}") from exc

@app.post("/chat")
async def chat(
    question: str = Form(...),
    breed   : str = Form(None),
    history : str = Form(None)
):
    import json
    history_list = []
    if history:
        try:
            history_list = json.loads(history)
        except Exception:
            history_list = []

    answer = ask_chatbot(question, breed, history_list)
    return {"answer": answer}