just a trial run for a movie site backend

#to run it in render:

1. fork the project
2. in render, add web service, backend, git repo, authorise
3. select the your forked repo
4. change the config settings: 
   start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   build command: `pip install -r requirements.txt`
   add env variable: key: REDIS_URL, value: redis://default:xyz@abc.db.redis.io:12125 from the redis dashboard
5. deploy

#to check if it's working

1. got to https://xyz.onrender.com/docs and manually put values on set or use the get command
2. just go to https://moviebase-backend-0c76.onrender.com/get/<replace-this-with-key> in your browser if a key, value pair is already set
3. if not set, set it first by step 1 or by running
   `curl -X POST "https://xyz.onrender.com/set" -H "Content-Type: application/json" -d '{"key": "movie_1", "value": "Interceptor"}'`
