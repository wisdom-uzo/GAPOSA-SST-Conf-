import os
from flask import Flask, render_template, session, g
from config import Config
from app.firebase_service import firebase_service

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Firebase service
    firebase_service.init_app(app)

    # Ensure upload folder exists safely
    upload_folder = app.config.get('LOCAL_UPLOAD_FOLDER')
    if upload_folder:
        try:
            os.makedirs(os.path.join(upload_folder, 'papers'), exist_ok=True)
            os.makedirs(os.path.join(upload_folder, 'receipts'), exist_ok=True)
            os.makedirs(os.path.join(upload_folder, 'speakers'), exist_ok=True)
        except OSError:
            pass

    # Register Blueprints
    from app.blueprints.main.routes import main_bp
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.registration.routes import reg_bp
    from app.blueprints.submissions.routes import sub_bp
    from app.blueprints.user.routes import user_bp
    from app.blueprints.admin.routes import admin_bp
    from app.blueprints.api.routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(reg_bp, url_prefix='/registration')
    app.register_blueprint(sub_bp, url_prefix='/submissions')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Jinja Filters
    @app.template_filter('number_format')
    def number_format_filter(value):
        if value is None or value == '' or str(value).strip() == '':
            return "0"
        try:
            return f"{float(value):,.0f}"
        except (ValueError, TypeError):
            return str(value)

    @app.template_filter('format_currency')
    def format_currency_filter(amount, currency='NGN'):
        if amount is None or amount == '' or str(amount).strip() == '':
            return "Free"
        try:
            num = float(amount)
            curr = str(currency).upper() if currency else 'NGN'
            if curr == 'USD':
                return f"${int(num) if num.is_integer() else f'{num:.2f}'}"
            return f"₦{num:,.0f}"
        except (ValueError, TypeError):
            return str(amount)

    @app.template_filter('format_date')
    def format_date_filter(date_val):
        if not date_val:
            return ""
        try:
            from datetime import datetime
            if isinstance(date_val, str):
                if 'T' in date_val:
                    dt = datetime.fromisoformat(date_val.replace('Z', '+00:00'))
                else:
                    dt = datetime.strptime(date_val, '%Y-%m-%d')
                return dt.strftime('%d %B, %Y')
            return str(date_val)
        except Exception:
            return str(date_val)

    @app.template_filter('status_badge_class')
    def status_badge_class_filter(status):
        status_map = {
            'Accepted': 'bg-emerald-100 text-emerald-800 border-emerald-300 dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-800',
            'Camera-ready': 'bg-teal-100 text-teal-800 border-teal-300 dark:bg-teal-950/50 dark:text-teal-300 dark:border-teal-800',
            'Under Review': 'bg-amber-100 text-amber-800 border-amber-300 dark:bg-amber-950/50 dark:text-amber-300 dark:border-amber-800',
            'Submitted': 'bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-950/50 dark:text-blue-300 dark:border-blue-800',
            'Revision Required': 'bg-orange-100 text-orange-800 border-orange-300 dark:bg-orange-950/50 dark:text-orange-300 dark:border-orange-800',
            'Rejected': 'bg-rose-100 text-rose-800 border-rose-300 dark:bg-rose-950/50 dark:text-rose-300 dark:border-rose-800',
            'Confirmed': 'bg-emerald-100 text-emerald-800 border-emerald-300 dark:bg-emerald-950/50 dark:text-emerald-300 dark:border-emerald-800',
            'Pending': 'bg-yellow-100 text-yellow-800 border-yellow-300 dark:bg-yellow-950/50 dark:text-yellow-300 dark:border-yellow-800'
        }
        return status_map.get(status, 'bg-slate-100 text-slate-800 border-slate-300 dark:bg-slate-800 dark:text-slate-300')

    # Context Processors
    @app.context_processor
    def inject_global_vars():
        current_user = None
        user_id = session.get('user_id')
        if user_id:
            current_user = firebase_service.get_user_by_id(user_id)

        active_fee_tier = Config.get_current_local_fee_tier()

        return {
            'config': app.config,
            'current_user': current_user,
            'active_fee_tier': active_fee_tier,
            'is_admin': current_user.get('role') == 'admin' if current_user else False,
            'is_author': current_user.get('role') in ['author', 'admin'] if current_user else False
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    return app
