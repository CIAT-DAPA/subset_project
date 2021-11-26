import requests

request_body = {
    #"crop": ["60818b1efc024440e44621d3", "60818b1efc024440e44621b9"], "country_name": ["Mexico"]
    "crop": ["60818b1efc024440e44621b2"]
}

print(request_body)

response = requests.post('http://localhost:5001/api/v1/accessions',json=request_body)


print(response.content)