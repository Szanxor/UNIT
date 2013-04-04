import tornado.web
import tornado.websocket
import tornado.ioloop
import thread
import zmq
import re


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("main.html")

class TestsHandler(tornado.web.RequestHandler):
    def get(self):
	tests = ["Test 1", "Test 2", "Test 3", "Test 4", "Test 5"]
        self.render("tests.html", tests=tests)

class LogHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        thread.start_new_thread(self.work, ())

    def work(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect("tcp://localhost:5556")
        socket.setsockopt(zmq.SUBSCRIBE, "")

        while True:
            message = socket.recv()
            self.write_message(message)


class ProgressHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        thread.start_new_thread(self.work, ())

    def on_message(self, message):
        if (message == 'start'):
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://localhost:5555")
            socket.send("process")
            socket.recv()

    def work(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect("tcp://localhost:5556")
        socket.setsockopt(zmq.SUBSCRIBE, "")

        while True:
            message = socket.recv()
            percent = re.match(r"(\d+)%$", message)
            if (percent and percent.group(1)):
                self.write_message(percent.group(1))


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/progress", ProgressHandler),
    (r"/log", LogHandler),
    (r"/tests", TestsHandler),
])


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
