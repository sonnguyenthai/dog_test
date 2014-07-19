try:
    import json
except ImportError:
    import simplejson as json
import base64
import Image
from cStringIO import StringIO
from sqlalchemy.orm.exc import NoResultFound
import tornado.ioloop
import tornado.web
from tornado.template import  Template

from models import db_session, Dog


def json_request(request):
    """
    Return a json object of request body or None
    """
    try:
        return json.loads(request.body)
    except:
        return None


def resize_image(buf):
    """
    Resize an image for downsampling with max-size: 100x100 px. Return base64
    encoded string of the image.
    """
    file_like = StringIO(base64.b64decode(buf))

    image = Image.open(file_like)
    maxSize = (100, 100)
    image.thumbnail(maxSize, Image.ANTIALIAS)
    resizedImageFile = StringIO()
    image.save(resizedImageFile , 'JPEG', optimize = True)
    resizedImageFile.seek(0)
    encode = base64.b64encode(resizedImageFile.getvalue())
    return encode



class CreateDog(tornado.web.RequestHandler):

    def post(self):
        data = json_request(self.request)
        if data:
            name = data.get("name", "")
            img = data.get("image", None)
            if not name or not img:
                self.write({"code": 0, "message": "Invalid input data: %s" %data})
            dog = Dog(name, resize_image(img))
            db_session.add(dog)
            db_session.commit()
            self.write({"code": 1, "message": "Dog created. ID: %s" %dog.id})
        else:
            self.write({"code": 0, "message": "Input data must be json"})


    def get(self):
        dogs = []
        for dog in db_session.query(Dog):
            item = {}
            item['name'] = dog.name
            item['image'] = self.request.host + dog.get_image_url()
            dogs.append(item)
        if dogs:
            self.write({"code": 1,
                    "message": "%s dogs found" %len(dogs),
                    "dogs": dogs})
        else:
            self.write({"code": 0, "message": "There is not dog found"})




class UpdateDog(tornado.web.RequestHandler):

    def get(self, id):
        try:
            dog = db_session.query(Dog).filter(Dog.id == id).one()
            data = {}
            data["name"] = dog.name
            data["image"] =  self.request.host + dog.get_image_url()
            self.write({"code": 1, "message": "Found", "Dog": str(data)})
        except NoResultFound:
            self.write({"code": 0, "message": "Dog not found"})
        except:
            self.write({"code": 0, "message": "Internal server error"})


    def put(self, id):
        try:
            dog = db_session.query(Dog).filter(Dog.id == id).one()
            data = json_request(self.request)
            if data:
                name = data.get("name", dog.name)
                img = data.get("image", dog.image)
                dog.image = resize_image(img)
                dog.name = name
                #db_session.add(dog)
                db_session.commit()
                self.write({"code": 1, "message": "Dog updated. ID: %s" %dog.id})
            else:
                self.write({"code": 0, "message": "Input data must be json"})
        except NoResultFound:
            self.write({"code": 0, "message": "Dog not found"})
        except:
            self.write({"code": 0, "message": "Internal server error"})



class DogImage(tornado.web.RequestHandler):

    def get(self, id):
        try:
            dog = db_session.query(Dog).filter(Dog.id == id).one()
            t = Template('<img alt="dog_image" src="data:image/jpeg;base64,{{ img }}" />')
            self.write(t.generate(img=dog.image))
        except:
            self.write("Dog not found")



class Home(tornado.web.RequestHandler):

    def get(self):
        self.write("I love dogs")



if __name__ == '__main__':
    try:
        print "Start the service"
        app = tornado.web.Application([
            (r'/dogs/?', CreateDog),
            (r'/dog/(\d+)/?', UpdateDog),
            (r'/dog/(\d+)/image/?', DogImage),
            (r'/?', Home)
            ])
        app.listen(8080)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print "\nStop the service"