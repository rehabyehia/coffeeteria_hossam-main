from fastapi import APIRouter, Body,Depends,status
from lib.crypto import create_access_token,get_password_hash
from models.runtime import ServiceResponse
from database.mongo_driver import get_database
from typing import Annotated
from fastapi.security import  OAuth2PasswordRequestForm
from database.user_database import validate_user,create_user
from datetime import  timedelta
import database.user_database as user_database
from models.token import Token
from models.user import User
from lib.crypto import auth_user


router = APIRouter()

async def get_userid(username):
    id=await get_database().get_collection('user').find_one({'username':username},{ "id": {"$toString": "$_id"},'_id':0})
    
    return  id['id']

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token|ServiceResponse:
    valid = await validate_user(form_data.username,form_data.password)
    if not valid:
        return ServiceResponse(success=False,msg="no such user", status_code=404)

    userid = await get_userid(form_data.username)
    access_token_expires = timedelta(minutes=1000000000)
    access_token = create_access_token(
        data={'userId':userid}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token)


@router.post('/signup')
async def signup(user:User =Body(embed=True)):
    try:
        return await create_user(user)
    except:
        return ServiceResponse(success=False,msg="couldn't add user",status_code=400)



@router.post('/personal_info')
async def personal_info(userId:str = Depends(auth_user)):
    res =  await user_database.personal_info(userId)
    return res

