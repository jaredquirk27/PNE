from google import genai

API_KEY = "AQ.Ab8RN6LYm6X17CnFYlykde5UgBA_QTRzrXMv4Yj73O4Uw8NAhw"

client = genai.Client(
    api_key=API_KEY
)

def generate_response(prompt):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text