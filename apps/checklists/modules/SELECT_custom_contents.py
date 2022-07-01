from pyexpat import model
from tkinter import INSERT
from numpy import record
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from datetime import timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import cx_Oracle
import os
import sys
import inspect
# import DAO
import apps.checklists.modules.DAO as DAO

import datetime
import json


class SelectCustomContents():
    def __init__(self):
        pass

    def select_team_leaders_tasks(self, userid):
        """
        組長タスクの抜出：
        LstUserCustomExecutionContentsの

        Parameters
        ----------
        userid: str
        組長のユーザーID

        return
        ----------
        records : list
        タスクが格納されたlist
        """

        # 対象のユーザー
        userid = userid
        # 引数
        model = DAO.DAO().LstUserCustomExecutionContents
        column = [model.user_account_id, model.is_using]
        target_element = [userid, 1]
        # 対象のユーザー設定情報を取得する
        results = DAO.DAO().method.select_where_and(DAO.DAO().session,
                                                    model, column, target_element)

        return results

    def select_daily_info(self, custom_execution_contents_id):
        """
        Dailyタスクの時間抜出:

        Parameters
        ----------
        custom_execution_contents_id: list
        組長タスクのIDを含むリスト
        [int,int,int,...]

        return
        ----------
        records : list
        それぞれのタスクに対応したdailyテーブルの要素が格納されたlist
        """

        # モデル
        model = DAO.DAO().LstDaily
        # 引数
        column = []
        for i in range(len(custom_execution_contents_id)):
            column.append(model.custom_execution_contents_id)
        target_element = custom_execution_contents_id
        results = DAO.DAO().method.select_where_or(DAO.DAO().session,
                                                   model, column, target_element)

        return results


if __name__ == "__main__":
    # InsertData = SelectCustomContents()
    # # info =[1,2,3]
    # records = InsertData.select_team_leaders_tasks(1)
    # print(records)
    # print(len(records))
    # for i in range(len(records)):
    #     print(records[i].create_date)
    #     print(records[i].custom_execution_contents_id)
    pass
