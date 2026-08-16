import os
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.firebase_service import firebase_service
from config import Config

reg_bp = Blueprint('registration', __name__)

def calculate_conference_fee(category_key, check_date=None):
    """Calculate fee amount and currency for a chosen category."""
    if check_date is None:
        check_date = date.today()

    if category_key == 'local_scholar':
        category_key = Config.get_current_local_fee_tier(check_date)

    tier_info = Config.FEES.get(category_key, Config.FEES['local_scholar_mid'])
    currency = tier_info.get('currency', 'NGN')
    amount = tier_info.get('amount_usd') if currency == 'USD' else tier_info.get('amount_ngn')

    return {
        'category_key': category_key,
        'category_name': tier_info.get('name'),
        'amount': amount,
        'currency': currency,
        'symbol': tier_info.get('symbol', '₦'),
        'description': tier_info.get('description', '')
    }

@reg_bp.route('/register', methods=['GET', 'POST'])
def register_conference():
    active_tier_key = Config.get_current_local_fee_tier()
    
    # Pre-fill user data if logged in
    current_user = None
    if session.get('user_id'):
        current_user = firebase_service.get_user_by_id(session.get('user_id'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        title = request.form.get('title', 'Mr.')
        affiliation = request.form.get('affiliation', '').strip()
        department = request.form.get('department', '').strip()
        country = request.form.get('country', 'Nigeria').strip()
        mode = request.form.get('mode', 'Physical')  # Physical or Virtual
        category = request.form.get('category', 'local_scholar')
        special_requests = request.form.get('special_requests', '').strip()

        if not full_name or not email or not phone or not affiliation:
            flash('Please complete all required fields.', 'error')
            return render_template('registration/register_conference.html', fees=Config.FEES, active_tier_key=active_tier_key, user=current_user)

        # Calculate exact fee
        fee_data = calculate_conference_fee(category)

        reg_data = {
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'title': title,
            'affiliation': affiliation,
            'department': department,
            'country': country,
            'mode': mode,
            'category_key': fee_data['category_key'],
            'category_name': fee_data['category_name'],
            'fee_amount': fee_data['amount'],
            'currency': fee_data['currency'],
            'currency_symbol': fee_data['symbol'],
            'special_requests': special_requests,
            'payment_status': 'Pending',
            'transaction_ref': '',
            'payment_proof_url': None,
            'user_id': session.get('user_id')
        }

        created_reg = firebase_service.create_registration(reg_data)
        flash(f"Registration initialised! Your Registration ID is {created_reg['id']}.", 'success')
        return redirect(url_for('registration.payment', reg_id=created_reg['id']))

    return render_template(
        'registration/register_conference.html',
        fees=Config.FEES,
        active_tier_key=active_tier_key,
        user=current_user
    )

@reg_bp.route('/payment/<reg_id>', methods=['GET', 'POST'])
def payment(reg_id):
    reg = firebase_service.get_registration(reg_id)
    if not reg:
        flash('Registration record not found.', 'error')
        return redirect(url_for('registration.register_conference'))

    if request.method == 'POST':
        transaction_ref = request.form.get('transaction_ref', '').strip()
        payment_proof_file = request.files.get('payment_proof')
        
        proof_url = None
        if payment_proof_file and payment_proof_file.filename:
            upload_res = firebase_service.upload_file(payment_proof_file, subfolder='receipts')
            if upload_res:
                proof_url = upload_res.get('url')

        if not transaction_ref and not proof_url:
            flash('Please provide either a bank transaction reference or upload your payment receipt proof.', 'error')
            return render_template('registration/payment.html', reg=reg, bank=Config)

        # Update payment info
        firebase_service.update_registration_payment(
            reg_id=reg_id,
            payment_proof_url=proof_url,
            transaction_ref=transaction_ref,
            payment_status='Pending'  # Pending verification by Secretariat / Admin
        )

        flash('Payment details submitted successfully! The Secretariat will verify your payment.', 'success')
        return redirect(url_for('registration.confirmation', reg_id=reg_id))

    return render_template('registration/payment.html', reg=reg, bank=Config)

@reg_bp.route('/confirmation/<reg_id>')
def confirmation(reg_id):
    reg = firebase_service.get_registration(reg_id)
    if not reg:
        flash('Registration record not found.', 'error')
        return redirect(url_for('main.index'))

    return render_template('registration/confirmation.html', reg=reg)

@reg_bp.route('/slip/<reg_id>', endpoint='official_slip')
@reg_bp.route('/slip/<reg_id>')
def slip(reg_id):
    reg = firebase_service.get_registration(reg_id)
    if not reg:
        flash('Registration record not found.', 'error')
        return redirect(url_for('registration.register_conference'))
    return render_template('registration/slip.html', reg=reg)
