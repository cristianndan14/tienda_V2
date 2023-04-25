import os
from flask import current_app
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from isbnlib import isbn_from_words
from werkzeug.utils import secure_filename

from ..models.BookModel import BookModel
from ..models.AuthorModel import AuthorModel

from ..models.entities.book import Book

from ..consts import *


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower(
        ) in current_app.config['ALLOWED_EXTENSIONS']


def init_book(app, db):

    @app.route('/books')
    @login_required
    def book_list():
        try:
            books = BookModel.book_list(db)
            data = {
                'title': 'Book list',
                'books': books
            }

            return render_template('book_list.html', data=data)
        except Exception as ex:
            return render_template('errors/error.html', message=format(ex))

    @app.route('/books/add_book', methods=['GET', 'POST'])
    @login_required
    def add_book():
        if current_user.user_type_id.id == 1:
            try:
                authors = AuthorModel.author_list(db)
                data = {
                    'title': 'Author list',
                    'authors': authors
                }
                if request.method == 'POST':
                    isbn = isbn_from_words(request.form['Title'])
                    title = request.form['Title']
                    publication_date = request.form['Publication_date']
                    price = request.form['Price']
                    file = request.files.get('customFile')
                    id_author = request.form['id_author']
                    filename = ''
                    cover_route = ''

                    if file.filename == '':
                        cover_route = '/img/covers/not-cover.png'
                    else:
                        filename = secure_filename(file.filename)
                        if not allowed_file(filename):
                            flash(FILE_NOT_SUPPORTED, 'warning')
                            return redirect(url_for('add_book'))
                        cover_route = f'/img/covers/{filename}'
                        file.save(os.path.join(
                            current_app.config['UPLOAD_COVERS'], filename))

                    new_book = Book(isbn, title, id_author,
                                    publication_date, price, cover_route)
                    add_book = BookModel.add_book(db, new_book)

                    if add_book != None:
                        flash(ADD_BOOK_SUCCESS, 'success')
                        return redirect(url_for('book_list'))
                    else:
                        return render_template('add_book.html')

                return render_template('add_book.html',
                                       data=data,
                                       )

            except Exception as ex:
                return render_template('errors/error.html', message=format(ex))
        else:
            return redirect(url_for('books'))
