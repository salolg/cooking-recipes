from py2neo import Graph, Node, Relationship
from passlib.hash import bcrypt
from datetime import datetime
import uuid
import os

url = os.environ.get("GRAPHENEDB_URL", "http://localhost:7474")
graph = Graph(url + "/db/data/")

class User:
    def __init__(self, username):
        self.username = username

    def find(self):
        user = graph.find_one("User", "username", self.username)
        return user
    def register(self, password):
        if not self.find():
            user = Node("User", username=self.username, password=bcrypt.encrypt(password))
            graph.create(user)
            return True
        return  False

    def verify_password(self, password):
        user = self.find()

        if not user:
            return False
        return bcrypt.verify(password, user["password"])

    def add_post(self, title, tags, text):
        user = self.find()
        today = datetime.now()
        post =Node(
            "Post",
            id=str(uuid.uuid4()),
            title=title,
            text=text,
            date=today.strftime('%Y-%m-%d')
        )

        rel = Relationship(user, "PUBLISHED", post)
        graph.create(rel)

        tags = [x.strip() for x in tags.lower().split(",")]
        tags = set(tags)

        for tag in tags:
            t = graph.merge_one("Tag", "name", tag)
            rel = Relationship(t, "TAGGED", post)
            graph.create(rel)

    def recent_posts(self):
        query = """
        MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
        WHERE user.username = {username}
        RETURN post, COLLECT(tag.name) AS tags
        ORDER BY post.timestamp
        """

        return graph.cypher.execute(query, username=self.username)

def todays_recent_posts(n):
    query = """
    MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
    WHERE post.date = {today}
    RETURN user.username AS username, post, COLLECT(tag.name) AS tags
    ORDER BY post.timestamp DESC LIMIT {n}
    """

    today = datetime.now().strftime('%Y-%m-%d')
    return graph.cypher.execute(query, today=today, n=n)

def searching_for_posts(tag):
    query = """
    MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
    WHERE tag.name = {tag}
    RETURN user.username AS username, post, COLLECT(tag.name) AS tags
    ORDER BY post.timestamp
    """

    return graph.cypher.execute(query, tag=tag)