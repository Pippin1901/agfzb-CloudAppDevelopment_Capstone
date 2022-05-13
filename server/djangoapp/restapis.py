import requests
import json

from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth

def get_request(url, **kwargs):
    #print(kwargs)
    print("GET from {} ".format(url))
    json_data={}
    try:
        if "apikey" in kwargs:
            response = requests.get(url, headers={'Content-Type':'application/json'}, params=kwargs, auth=HTTPBasicAuth("apikey", kwargs["apikey"]))
        else:
            response = requests.get(url, headers={'Content-Type':'application/json'}, params=kwargs)

        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        #print(json_data)
    except Exception as e:
        print("Error " ,e)
    
    return json_data

def post_request(url, payload, **kwargs):
    print(url)
    print(payload)
    print(kwargs)
    try:
        response = requests.post(url, params=kwargs, json=payload)
    except Exception as e:
        print("Error" ,e)
    print("Status Code ", {response.status_code})
    data = json.loads(response.text)
    return data

def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    #print(json_result)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["entries"]
        # For each dealer object
        for dealer_doc in dealers:
            # Get its content in `doc` object
            #dealer_doc = dealers["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealer_id)
    
    if "entries" in json_result:
        reviews = json_result["entries"]
        # For each review object
        for review in reviews:
            review_obj = DealerReview(
                dealership=review["dealership"],
                name=review["name"],
                purchase=review["purchase"],
                review=review["review"],
                purchase_date=review["purchase_date"],
                car_make=review["car_make"],
                car_model=review["car_model"],
                car_year=review["car_year"],
                sentiment=analyze_review_sentiments(review["review"]),
                id=review['id']
                )
            results.append(review_obj)
    #print(results[0])
    return results

def analyze_review_sentiments(dealerreview, **kwargs):
    API_KEY="MxFCXuNdAY4i7RdB1PTx0LGspyMbNVmVOKxtpJ5XPxkz"
    #API_KEY="0614ccd0-1e9f-4d49-923e-e7741f963747:Q3ZX2R1b3oBEb0XebEO99rpulJ31yoY7X5GfjoQykN4RpM9eThYrrs14If0aOHtG"
    NLU_URL='https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/93a549ab-8f15-404e-a8ed-97f6fb8a35aa/v1/analyze?version=2020-08-01'
    params = json.dumps({"text": dealerreview, "features": {"sentiment": {}}})
    response = requests.post(NLU_URL,data=params,headers={'Content-Type':'application/json'},auth=HTTPBasicAuth("apikey", API_KEY))
    
    #print(response.json())
    try:
        sentiment=response.json()['sentiment']['document']['label']
        return sentiment
    except:
        return "neutral"
