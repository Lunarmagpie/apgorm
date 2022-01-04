# MIT License
#
# Copyright (c) 2021 TrigonDev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

from pathlib import Path

import apgorm
from apgorm.sql.generators.comp import neq
from apgorm.types.character import VarChar


class User(apgorm.Model):
    username = VarChar(32).field()
    nickname = VarChar(32).nullablefield()

    primary_key = (username,)


class Database(apgorm.Database):
    users = User


async def _main(db: Database):
    # create a user
    user = User(username="Circuit")
    await user.create()

    # get the user
    _u = await User.fetch(username="Circuit")
    assert user == _u

    # delete the user
    await user.delete()

    # create lots of users
    for un in ["Circuit", "Bad Guy", "Super Man"]:
        await User(username=un).create()

    # get all users except for "Bad Guy"
    query = User.fetch_query()
    query.where(neq(User.username, "Bad Guy"))
    good_users = await query.fetchmany()

    # set the nickname for all good users to "Good Guy"
    for user in good_users:
        user.nickname.v = "Good Guy"
        await user.save()

    # OR, you can use User.update_query...
    (
        await User.update_query()
        .where(neq(User.username, "Bad Guy"))
        .set(nickname="Good Guy")
        .execute()
    )

    # delete all users
    await User.delete_query().execute()


async def main():
    db = Database(Path("examples/basic/migrations"))
    await db.connect(database="apgorm")

    if db.must_create_migrations():
        db.create_migrations()
    if await db.must_apply_migrations():
        await db.apply_migrations()

    try:
        await _main(db)
    finally:
        await db.cleanup()