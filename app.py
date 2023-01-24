from flask import Flask,request,Response, Request, render_template
import pymongo
import json
from bson.objectid import ObjectId
from urllib.parse import urlparse,parse_qs

app=Flask(__name__)

try:
    #mongo=pymongo.MongoClient(host='localhost',port=27017,serverSelectionTimeoutMS=1000)
    conn_str='mongodb+srv://shilpa2468:shilpa2468@cluster0.unwlntb.mongodb.net/?retryWrites=true&w=majority'
    mongo=pymongo.MongoClient(conn_str)
    db=mongo.newsdb
    news=db.news
    mongo.server_info()
    print("connection successfull")
except:
    print('Cant connect to db')

def fuzzytitle(q):
    result=news.aggregate([
        {
            '$search':{
                'index':'news_search',
                'text':{
                    'query':q,
                    'path':'title',
                    'fuzzy':{}
                }
            }
        }
    ])
    return list(result)

def fuzzydescp(q):
    result=news.aggregate([
        {
            '$search':{
                'index':'news_search',
                'text':{
                    'query':q,
                    'path':'description',
                    'fuzzy':{}
                }
            }
        }
    ])
    return list(result)

def fuzzycontent(q):
    result=news.aggregate([
        {
            '$search':{
                'index':'news_search',
                'text':{
                    'query':q,
                    'path':'content',
                    'fuzzy':{}
                }
            }
        }
    ])
    return list(result)

#getting news by keyword search
@app.route('/news/search',methods=['GET'])
def getnewsbykeyword():
    query=request.args.get('q',None)
    data1=fuzzytitle(query)
    data2=fuzzydescp(query)
    data3=fuzzycontent(query)
    #print(data)
    result=[]
    for d in data1:
        d['_id']=str(d['_id'])
        if d not in result:
            result.append(d)
    for d in data2:
        d['_id']=str(d['_id'])
        if d not in result:
            result.append(d)
    for d in data3:
        d['_id']=str(d['_id'])
        if d not in result:
            result.append(d)
    
    return Response(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )

# @app.route('/sample',methods=['GET'])
# def sample():
#     parseresult=urlparse(request.url)
#     d=parse_qs(parseresult.query)
#     s='{'
#     for a in d:
#         print(a,'->',d.get(a))
#         ss=''
#         ss=str(d.get(a))
#         ss=ss[1:(len(ss)-1)]
#         print(ss)
#         s=s+f'\'{a}\':{ss},'
#     s=s[0:(len(s)-1)]
#     s=s+'}'
#     print(s)
#     dbresponse=db.news.find_one(s)
#     print(dbresponse)
#     for everynews in dbresponse:
#         everynews['_id']=str(everynews['_id'])
#     return Response(
#         response=json.dumps(dbresponse),
#         status=200,
#         mimetype='application/json'
#     )

#posting news
@app.route('/news',methods=['POST'])
def postnews():
    data=request.get_json()
    newsdata={'author':data['author'],
        'title':data['title'],
        'description':data['description'],
        'url':data['url'],
        'urlToImage':data['urlToImage'],
        'publishedAt':data['publishedAt'],
        'content':data['content']}
    dbresponse=db.news.insert_one(newsdata)
    return Response(
        response=json.dumps({'message':'News inserted','ID':f'{dbresponse.inserted_id}'}),
        status=200,
        mimetype='application/json')

#getting all news
@app.route('/news',methods=['GET'])
def getnews():
    dbresponse=list(db.news.find())
    for everynews in dbresponse:
        everynews['_id']=str(everynews['_id'])
    return Response(
        response=json.dumps(dbresponse),
        status=200,
        mimetype='application/json'
    )

#getting news by id
@app.route('/news/<id>',methods=['GET'])
def getnewsbyid(id):
    dbresponse=db.news.find_one({'_id':ObjectId(id)})
    if dbresponse is None:
        return Response(
            response=json.dumps({'message':'No news with such ID'}),
            status=404,
            mimetype='application/json'
        )
    dbresponse['_id']=str(dbresponse['_id'])
    return Response(
        response=json.dumps(dbresponse),
        status=200,
        mimetype='application/json'
    )

#get news by author and title(query)
@app.route('/getnews')
def getnewsbytitleandauthor():
    parseresult=urlparse()
    print('URL',parseresult)
    author=request.args.get('author',None)
    title=request.args.get('title',None)
    print('*********',request.args)
    if None not in (author,title):
        dbresponse=db.news.find_one({'author':author,'title':title})
    elif author is not None:
        dbresponse=db.news.find_one({'author':author})
    elif title is not None:
        dbresponse=db.news.find_one({'title':title})
    if dbresponse is None:
        return Response(
            response=json.dumps({'message':'No news with such details'}),
            status=404,
            mimetype='application/json'
        )
    dbresponse['_id']=str(dbresponse['_id'])
    return Response(
        response=json.dumps(dbresponse),
        status=200,
        mimetype='application/json'
    )

if __name__=='__main__':
    app.run(port=5000,debug=True)