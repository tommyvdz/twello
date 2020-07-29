from flask import render_template, flash, redirect, request, g, jsonify, current_app
from flask.helpers import url_for
from flask_babel import get_locale, _, lazy_gettext as _l
from app import db
from app.main import bp
from app.translate import translate
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm, MessageForm, BoardForm, ListForm, CardForm
from app.models import User, Post, Message, Notification, Board, List, Card
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime
from guess_language import guess_language
from sqlalchemy import func

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data) # guess the language of the post, if unknown or unexpected long it is treated as unknown
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user,
                    language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post has been published'))
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)

    # paginate object returns .items with the content for a page, 
    # but also properties such as has_next, has_prev and next_num and prev_num 
    posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', title=_('Home'), form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title=_('Explore'), posts=posts.items, next_url=next_url, prev_url=prev_url)

@bp.route('/boards', methods=['GET', 'POST'])
@login_required
def boards():
    currentboards = current_user.created_boards
    form = BoardForm()
    if form.validate_on_submit():
        board = Board(name=form.name.data, creator=current_user)
        db.session.add(board)
        db.session.commit()
        flash(_('Your board has been created'))
        return redirect(url_for('main.boards'))

    return render_template('boards.html', boards=currentboards, form=form )

@bp.route('/board/<boardid>', methods=['GET', 'POST'])
@login_required
def board(boardid):
    board = Board.query.filter_by(id=boardid).first_or_404()
    listform = ListForm()
    cardform = CardForm()
    if listform.validate_on_submit() and listform.create.data:
        mpos = db.session.query(func.max(List.position)).scalar() #determine highest position number to increment the position
        list = List(name=listform.name.data, creator=current_user, board_id=board.id, position=mpos+1)
        db.session.add(list)
        db.session.commit()
        flash(_('Your list has been created'))
        return redirect(url_for('main.board', boardid=boardid))
    elif cardform.validate_on_submit() and cardform.add.data:
        mpos = db.session.query(func.max(Card.position)).scalar()
        card = Card(name=cardform.name.data, creator=current_user, position=mpos+1, list_id=List.query.filter_by(id=cardform.listid.data).first_or_404().id)
        db.session.add(card)
        db.session.commit()
        flash(_('Your card has been added'))
        return redirect(url_for('main.board', boardid=boardid))
    return render_template('board.html', board=board, listform=listform, cardform=cardform)

@bp.route('/updatecard', methods=['POST'])
@login_required
def updatecard():
    card = Card.query.filter_by(id=request.form['id']).first_or_404()
    card.list_id = request.form['targetlist']
    card.position = request.form['position']
    db.session.commit()
    resp = jsonify(success=True)
    return resp

@bp.route('/updatelist', methods=['POST'])
@login_required
def updatelist():
    list = List.query.filter_by(id=request.form['id']).first_or_404()
    list.position = request.form['position']
    db.session.commit()
    resp = jsonify(success=True)
    return resp

@bp.route('/deletelist', methods=['POST'])
@login_required
def deletelist():
    list = List.query.filter_by(id=request.form['id']).first_or_404()
    db.session.delete(list)
    db.session.commit()
    resp = jsonify(success=True)
    return resp

@bp.route('/deletecard', methods=['POST'])
@login_required
def deletecard():
    card = Card.query.filter_by(id=request.form['id']).first_or_404()
    db.session.delete(card)
    db.session.commit()
    resp = jsonify(success=True)
    return resp

@bp.route('/deleteboard', methods=['POST'])
@login_required
def deleteboard():
    board = Board.query.filter_by(id=request.form['id']).first_or_404()
    db.session.delete(board)
    db.session.commit()
    resp = jsonify(success=True)
    return resp

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items, form=form, next_url=next_url, prev_url=prev_url)
    

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'), form=form)

@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot follow yourself'))
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are now following %(username)s!',username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))

@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('No longer following %(username)s.',username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))

@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})

@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)
                           
@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    return render_template('user_popup.html', user=user, form=form)

@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user,
                      body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        
        flash(_('Your message has been sent.'))
        return redirect(url_for('main.user', username=recipient))
    return render_template('send_message.html', title=_('Send Message'),
                           form=form, recipient=recipient)

@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(
        Message.timestamp.desc()).paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url)

@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])

@bp.route('/export_posts')
@login_required
def export_posts():
    if current_user.get_task_in_progress('export_posts'):
        flash(_('An export task is currently in progress'))
    else:
        current_user.launch_task('export_posts', _('Exporting posts...'))
        db.session.commit()
    return redirect(url_for('main.user', username=current_user.username))