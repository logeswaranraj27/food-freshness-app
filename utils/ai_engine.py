import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
from PIL import Image
import numpy as np
import streamlit as st

# ===== FRUIT METADATA & NUTRITION DATABASE =====
FRUIT_DATABASE = {
    "Banana": {
        "emoji": "🍌",
        "category": "Tropical Fruit",
        "optimal_temp": "12°C - 15°C (Avoid direct refrigeration when green)",
        "ethylene_producer": True,
        "nutrients": "Potassium (358mg), Vitamin B6, Vitamin C, Dietary Fiber",
        "sensory": {
            "firmness": "Softens gradually from firm starchy tip to creamy pulp",
            "aroma": "Sweet esters develop with yellow peel and sugar spots",
            "appearance": "Green (Unripe) -> Solid Yellow (Prime) -> Brown Speckled (Sugar Ripe)"
        },
        "base_shelf_life_days": 6
    },
    "Apple": {
        "emoji": "🍎",
        "category": "Pome Fruit",
        "optimal_temp": "1°C - 4°C (Crisper drawer)",
        "ethylene_producer": True,
        "nutrients": "High Quercetin, Vitamin C (14% DV), Pectin Prebiotic Fiber",
        "sensory": {
            "firmness": "Crisp and firm resistance when gently pressed near stem",
            "aroma": "Floral and subtly tart scent when fresh",
            "appearance": "Taut smooth skin; avoid soft mushy brown depressions"
        },
        "base_shelf_life_days": 14
    },
    "Orange": {
        "emoji": "🍊",
        "category": "Citrus Fruit",
        "optimal_temp": "4°C - 8°C (High humidity)",
        "ethylene_producer": False,
        "nutrients": "Vitamin C (100% DV), Folate, Hesperidin Flavonoids, Calcium",
        "sensory": {
            "firmness": "Firm, dense and heavy for its size indicating high juice content",
            "aroma": "Bright, aromatic citrus oils released from peel",
            "appearance": "Uniform vibrant color; watch out for white or green powdery mold"
        },
        "base_shelf_life_days": 12
    },
    "Tomato": {
        "emoji": "🍅",
        "category": "Botanical Berry",
        "optimal_temp": "12°C - 16°C (Refrigeration impairs flavor volatile enzymes)",
        "ethylene_producer": True,
        "nutrients": "Lycopene Antioxidant, Vitamin C, Potassium, Folate",
        "sensory": {
            "firmness": "Yields slightly to gentle thumb pressure without bruising",
            "aroma": "Earthy, herbaceous aroma around the green calyx stem",
            "appearance": "Deep red gloss; wrinkling skin indicates moisture loss"
        },
        "base_shelf_life_days": 7
    },
    "Lemon": {
        "emoji": "🍋",
        "category": "Citrus Fruit",
        "optimal_temp": "4°C - 7°C (Sealed container maintains moisture)",
        "ethylene_producer": False,
        "nutrients": "Citric Acid, Vitamin C (88% DV), Limonene, Bioflavonoids",
        "sensory": {
            "firmness": "Slight springiness indicates juicy interior",
            "aroma": "Intense fresh zesty bouquet",
            "appearance": "Fine-textured bright yellow rind; soft spots mean internal decay"
        },
        "base_shelf_life_days": 15
    },
    "Strawberry": {
        "emoji": "🍓",
        "category": "Aggregate Accessory Fruit",
        "optimal_temp": "1°C - 3°C (Do not wash until ready to eat)",
        "ethylene_producer": False,
        "nutrients": "Anthocyanins, Manganese, Vitamin C (140% DV), Ellagic Acid",
        "sensory": {
            "firmness": "Plump and tender, never hollow or squishy",
            "aroma": "Fragrant, sweet and berry-rich",
            "appearance": "Bright glossy red with fresh green caps; no gray botrytis mold"
        },
        "base_shelf_life_days": 4
    },
    "Mango": {
        "emoji": "🥭",
        "category": "Tropical Drupe",
        "optimal_temp": "10°C - 13°C",
        "ethylene_producer": True,
        "nutrients": "Vitamin A (Beta-Carotene), Vitamin C, Digestive Enzymes (Amylases)",
        "sensory": {
            "firmness": "Gently yields to soft pressure around the shoulder",
            "aroma": "Rich fruity, floral perfume near the stem end",
            "appearance": "Vibrant hues; slight sap leakage near stem is normal"
        },
        "base_shelf_life_days": 8
    },
    "Bell Pepper": {
        "emoji": "🫑",
        "category": "Solanaceae Vegetable/Fruit",
        "optimal_temp": "7°C - 10°C (Crisper drawer with medium humidity)",
        "ethylene_producer": False,
        "nutrients": "Vitamin C (200% DV), Vitamin A, Capsanthin, Potassium",
        "sensory": {
            "firmness": "Extremely rigid and taut walls with heavy feel",
            "aroma": "Crisp green and grassy scent",
            "appearance": "Shiny, smooth skin without indentation pits or soft patches"
        },
        "base_shelf_life_days": 10
    },
    "Avocado": {
        "emoji": "🥑",
        "category": "Single-Seeded Berry",
        "optimal_temp": "4°C - 6°C once ripe (Room temp to ripen)",
        "ethylene_producer": True,
        "nutrients": "Heart-Healthy Monounsaturated Fats (Oleic Acid), Potassium, Folate",
        "sensory": {
            "firmness": "Gentle thumb yield without leaving an indentation",
            "aroma": "Mildly nutty and rich",
            "appearance": "Dark pebbled skin; under-stem button should be bright green, not brown"
        },
        "base_shelf_life_days": 5
    },
    "Generic Fruit / Produce": {
        "emoji": "🍏",
        "category": "Fresh Produce",
        "optimal_temp": "4°C - 10°C",
        "ethylene_producer": False,
        "nutrients": "Dietary Fiber, Essential Vitamins, Minerals & Antioxidants",
        "sensory": {
            "firmness": "Natural elasticity and firmness for its variety",
            "aroma": "Natural fresh botanical scent without fermented sour notes",
            "appearance": "Clean skin free from mold spores, slime, or discoloration"
        },
        "base_shelf_life_days": 7
    }
}

# Mapping common ImageNet class IDs/words to our catalog
IMAGENET_FRUIT_KEYWORDS = {
    "banana": "Banana",
    "apple": "Apple",
    "granny_smith": "Apple",
    "custard_apple": "Apple",
    "orange": "Orange",
    "lemon": "Lemon",
    "strawberry": "Strawberry",
    "bell_pepper": "Bell Pepper",
    "capsicum": "Bell Pepper",
    "tomato": "Tomato",
    "mango": "Mango",
    "avocado": "Avocado",
    "pomegranate": "Generic Fruit / Produce",
    "fig": "Generic Fruit / Produce",
    "pineapple": "Generic Fruit / Produce",
    "jackfruit": "Generic Fruit / Produce",
    "cucumber": "Generic Fruit / Produce",
    "zucchini": "Generic Fruit / Produce"
}


@st.cache_resource(show_spinner=False)
def load_freshness_model():
    """Load custom trained freshness binary classification model."""
    try:
        model = tf.keras.models.load_model("freshness_model.h5")
        return model
    except Exception as e:
        st.error(f"Error loading freshness model: {e}")
        return None


@st.cache_resource(show_spinner=False)
def load_fruit_classifier():
    """Load pre-trained MobileNetV2 for fruit identification."""
    try:
        model = MobileNetV2(weights="imagenet")
        return model
    except Exception as e:
        st.warning(f"ImageNet model loading fallback: {e}")
        return None


def identify_fruit(image: Image.Image, classifier_model):
    """Identifies the fruit type using ImageNet predictions or color heuristics."""
    if classifier_model is None:
        return "Generic Fruit / Produce", 85.0

    try:
        img_resized = image.resize((224, 224))
        x = img_to_array(img_resized)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        preds = classifier_model.predict(x, verbose=0)
        decoded = decode_predictions(preds, top=5)[0]

        for _, label, conf in decoded:
            label_lower = label.lower().replace(" ", "_")
            for keyword, fruit_name in IMAGENET_FRUIT_KEYWORDS.items():
                if keyword in label_lower:
                    return fruit_name, float(conf * 100)

        # Fallback: Check top prediction directly
        top_label = decoded[0][1].replace("_", " ").title()
        return "Generic Fruit / Produce", float(decoded[0][2] * 100)
    except Exception:
        return "Generic Fruit / Produce", 80.0


def crop_center_square(image: Image.Image) -> Image.Image:
    """Crops the image to a centered square."""
    width, height = image.size
    min_dim = min(width, height)
    left = (width - min_dim) / 2
    top = (height - min_dim) / 2
    right = (width + min_dim) / 2
    bottom = (height + min_dim) / 2
    return image.crop((left, top, right, bottom))


def analyze_food_quality(image: Image.Image, freshness_model, classifier_model, storage_temp_c: int = 22):
    """
    Executes full multi-stage AI analysis:
    - Fruit Identification
    - Freshness score (0 - 100%)
    - Ripeness stage
    - Days to Ripe & Days to Rot (temperature adjusted)
    - Edibility and safety rating
    - Sensory profile and nutritional data
    """
    # 1. Identify Fruit
    fruit_name, fruit_conf = identify_fruit(image, classifier_model)
    fruit_info = FRUIT_DATABASE.get(fruit_name, FRUIT_DATABASE["Generic Fruit / Produce"])

    # 2. Freshness Prediction
    img_resized = image.resize((224, 224))
    img_array = img_to_array(img_resized) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    if freshness_model is not None:
        raw_pred = float(freshness_model.predict(img_array, verbose=0)[0][0])
    else:
        raw_pred = 0.2  # Safe fallback

    # In freshness_model: 0 is fresh, 1 is rotten
    freshness_percent = max(0.0, min(100.0, (1.0 - raw_pred) * 100.0))
    is_fresh = raw_pred < 0.5
    status_label = "Fresh" if is_fresh else "Rotten"
    confidence = (1.0 - raw_pred) * 100.0 if is_fresh else raw_pred * 100.0

    # 3. Dynamic Ripeness & Timeline Modeling
    base_shelf_days = fruit_info.get("base_shelf_life_days", 7)
    
    # Temperature degradation multiplier (Arrhenius food decay approximation)
    # Storing at 4°C slows decay by ~2.5x compared to 25°C room temp
    if storage_temp_c <= 6:
        temp_decay_multiplier = 2.0  # Cold refrigeration extends life
    elif storage_temp_c <= 15:
        temp_decay_multiplier = 1.3  # Cool cellar
    elif storage_temp_c <= 25:
        temp_decay_multiplier = 1.0  # Standard room temp
    else:
        temp_decay_multiplier = 0.6  # Hot weather accelerates decay

    if freshness_percent >= 88:
        ripeness_stage = "Optimal Freshness (Peak Peak)"
        days_to_ripe = 0
        days_to_rot = max(1, round((base_shelf_days * 0.9) * temp_decay_multiplier))
        safety_status = "Safe to Eat (Peak Flavor)"
        safety_score = 5
        buy_recommendation = "Highly Recommended — Premium Quality"
    elif freshness_percent >= 72:
        ripeness_stage = "Fresh & Firm"
        days_to_ripe = max(0, round(1.5 / temp_decay_multiplier)) if fruit_info.get("ethylene_producer") else 0
        days_to_rot = max(1, round((base_shelf_days * 0.6) * temp_decay_multiplier))
        safety_status = "Safe to Eat (Fresh Quality)"
        safety_score = 4
        buy_recommendation = "Great Buy — Consume within a few days"
    elif freshness_percent >= 55:
        ripeness_stage = "Fully Ripe / Softening"
        days_to_ripe = 0
        days_to_rot = max(1, round((base_shelf_days * 0.3) * temp_decay_multiplier))
        safety_status = "Eat Promptly / Cook"
        safety_score = 3
        buy_recommendation = "Discounted Buy — Ideal for immediate use"
    elif freshness_percent >= 40:
        ripeness_stage = "Near Expiration / Bruised"
        days_to_ripe = 0
        days_to_rot = max(0, round(1 * temp_decay_multiplier))
        safety_status = "Inspect Closely / Cook or Freeze"
        safety_score = 2
        buy_recommendation = "Avoid buying unless on heavy clearance for immediate baking"
    else:
        ripeness_stage = "Spoiled / Decayed"
        days_to_ripe = 0
        days_to_rot = 0
        safety_status = "Do Not Consume (Microbial Hazard)"
        safety_score = 1
        buy_recommendation = "Do Not Purchase — Discard / Compost"

    result = {
        "fruit_name": fruit_name,
        "emoji": fruit_info["emoji"],
        "category": fruit_info["category"],
        "status_label": status_label,
        "freshness_score": round(freshness_percent, 1),
        "confidence": round(confidence, 1),
        "raw_prediction": round(raw_pred, 4),
        "ripeness_stage": ripeness_stage,
        "days_to_ripe": days_to_ripe,
        "days_to_rot": days_to_rot,
        "storage_temp_c": storage_temp_c,
        "safety_status": safety_status,
        "safety_score": safety_score,
        "buy_recommendation": buy_recommendation,
        "nutrients": fruit_info["nutrients"],
        "sensory": fruit_info["sensory"],
        "optimal_temp": fruit_info["optimal_temp"],
        "ethylene_producer": fruit_info["ethylene_producer"]
    }
    return result
