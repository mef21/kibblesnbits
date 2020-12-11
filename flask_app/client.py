import requests



class Dog(object):
    def __init__(self, pupjson, detailed=False):
        if detailed:
            self.imgs = pupjson["imglist"]
            self.sbs = pupjson["sblist"]
        
        self.breed = pupjson["Breed"]
        self.subbreed = pupjson["Subbreed"]
        self.type = "Dog"
        self.id_url = self.breed.lower()
        if(self.subbreed != ""):
            self.id_url += "1" + self.subbreed.lower()

    def __repr__(self):
        return self.id_url


class DogClient(object):
    def __init__(self):
        #self.sess = requests.Session()
        self.base_url = 'https://dog.ceo/api/'
    def _get(self,resource):
        """Sends a GET request to the provided resource and returns the 'message' data if it exists."""
        url = '{0}{1}'.format(self.base_url, resource)
        res = requests.get(url)
        return res

    def search(self, search_string):
        """
        Searches the API for the supplied search_string, and returns
        a list of Media objects if the search was successful, or the error response
        if the search failed.

        Only use this method if the user is using the search bar on the website.
        """
        if not isinstance(search_string, str):
            raise TypeError('Error Search query must be a string string')
        
        resp = self._get('breeds/list/all')

        if resp.status_code != 200:
            raise ValueError(
                "Search request failed; make sure your API key is correct and authorized"
            )
        
        data = resp.json()
        if data["message"] == {}:
            raise ValueError(f'[ERROR]: Error retrieving results: \'{data["Error"]}\' ')

        search_json = data["message"]
        breed_list = []
        s = search_string.split()
        
        page = 1
        results = {}
        remaining_results = 0
        re = []
        for i in range(0,len(s)):
            re.append(s[i].lower())
        s = re    
        for b in search_json.keys():
            if s[0] in b or s[0] == b or (len(s) == 2 and (s[1] in b or s[1] == b)):
                results[b] = {"Breed":None,"Poster":None}
                results[b]["Breed"] = b[0].upper() + b[1:]
                results[b]["Subbreed"] = ""
                remaining_results +=1
                for sb in search_json[b]:
                    if (len(s) == 2 and s[1] in sb) or (len(s) == 2 and (s[0] in sb or s[0] == sb)) or len(s) == 1:
                        results[b + " " + sb] = {"Breed":None,"Subbreed":None}
                        results[b + " " + sb]["Breed"] = b[0].upper() + b[1:]
                        results[b + " " + sb]["Subbreed"] = sb[0].upper() + sb[1:]
                        remaining_results += 1
        
        result = []
        if remaining_results == 0:
            raise ValueError(f'[ERROR]: Error retrieving results: There are no dog breeds or subbreeds in our databse matching your query.')
        ## We may have more results than are first displayed
        while remaining_results != 0:
            for item_json in results:
                result.append(Dog(results[item_json]))
                remaining_results -= 1
            page += 1
            
        return result

    def retrieve_dog_by_id(self, breed):
        """
        Use to obtain a Dog object representing the Dog identified by
        the supplied id_url
        """
        pjson = {"Breed":None,"Subbreed":None,"imglist":[],"sblist":[]}    
        subbreed = None
        if "1" in breed:
            s = breed.split("1")
            print(s)
            subbreed = s[1]
            breed = s[0]
        if not isinstance(breed, str):
            raise TypeError('breed must be a string')
        if subbreed == None:
            resp = self._get('breed/{0}/images'.format(breed))
            resp2 = self._get('breeds/list/all')
            pjson["Breed"] = breed
            pjson["Subbreed"] = ""
            if resp2.status_code == 200:
                data = resp2.json()
                pjson["sblist"] = data["message"][breed].copy()
        else:
            if not isinstance(subbreed, str):
                raise TypeError('subbreed must be a string')
            resp = self._get('breed/{0}/{1}/images'.format(breed, subbreed))
            pjson["Breed"] = breed
            pjson["Subbreed"] = subbreed
        
        if resp.status_code != 200:
            raise ValueError(
                "Search request failed; make sure your API key is correct and authorized"
            )

        data = resp.json()

        if data["status"] != "success":
            raise ValueError(f'Error retrieving results: \'{data["Error"]}\' ')
        if data["message"] == []:
            raise ValueError(f'No images were able to be pulled of this dog and breed')
        imgs = data["message"]
        #if len(imgs) > 25:
        #    imgs = imgs[0:26]
        
        pjson["imglist"]=imgs
        dog = Dog(pjson, detailed=True)

        return dog


## -- Example usage -- ###
if __name__ == "__main__":
    import os

    client = DogClient()

    dogs = client.search("guardians")

    for dog in dogs:
        print(dog)

    print(len(dogs))
