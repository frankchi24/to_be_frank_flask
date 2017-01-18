from FlaskApp.dbconnect import connection, connection_scripts
from sqlalchemy_mapping import scripts
from sqlalchemy import and_, or_, asc, desc


def get_list_of_shows():
    c, conn = connection_scripts()
    list_of_show = []
    c.execute("SELECT DISTINCT show_name FROM scripts;")
    for show in c:
        list_of_show.append(show)
    c.close()
    conn.close()
    return list_of_show


def search_scripts_sqlalchemy(page, select, title):
    title1 = '% ' + title + '%'
    title2 = title + ' %'
    if select == "all":
        rows = scripts.query.filter(or_(scripts.scripts.like(
            title1), scripts.scripts.like(title2))).paginate(page, 30, False)

    else:
        rows = scripts.query.filter(and_(scripts.show_name == select,
                                         or_(scripts.scripts.like(title1),
                                             scripts.scripts.like(title2))
                                         )
                                    ).paginate(page, 30, False)
    for row in rows.items:
        context1 = scripts.query.filter(
            scripts.sid < row.sid).order_by(desc(scripts.sid)).limit(2).all()
        context2 = scripts.query.filter(
            scripts.sid >= row.sid).order_by(asc(scripts.sid)).limit(2).all()
        context = context1 + context2
        test = ''
        for c in context:
            test = test + c.scripts
        row.footnote = test
    return rows


def header_image_path(title):
    path = {"How I Met Your Mother": 'img/tv_show_background.jpg',
            "House of Cards": 'img/tv_show_background.jpg',
            "Suits": 'img/tv_show_background.jpg',
            "Mad Men": 'img/tv_show_background.jpg', "The Big Bang Theory": 'img/tv_show_background.jpg',
            }
    search_header_path = path[title]
    return search_header_path
