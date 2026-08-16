/**
 * ICONFST'26 Interactive JavaScript Engine
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Menu Toggle
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // 2. User Dropdown Toggle
    const userDropdownBtn = document.getElementById('user-dropdown-btn');
    const userDropdown = document.getElementById('user-dropdown');
    if (userDropdownBtn && userDropdown) {
        userDropdownBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('hidden');
        });
        document.addEventListener('click', () => {
            if (!userDropdown.classList.contains('hidden')) {
                userDropdown.classList.add('hidden');
            }
        });
    }

    // 3. Conference Countdown Timer (Target: August 23, 2026 09:00:00 UTC+1)
    const countdownContainer = document.getElementById('conference-countdown');
    if (countdownContainer) {
        const targetDate = new Date('2026-08-23T09:00:00+01:00').getTime();

        const updateCountdown = () => {
            const now = new Date().getTime();
            const difference = targetDate - now;

            if (difference > 0) {
                const days = Math.floor(difference / (1000 * 60 * 60 * 24));
                const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((difference % (1000 * 60)) / 1000);

                const daysEl = document.getElementById('cd-days');
                const hoursEl = document.getElementById('cd-hours');
                const minutesEl = document.getElementById('cd-minutes');
                const secondsEl = document.getElementById('cd-seconds');

                if (daysEl) daysEl.textContent = String(days).padStart(2, '0');
                if (hoursEl) hoursEl.textContent = String(hours).padStart(2, '0');
                if (minutesEl) minutesEl.textContent = String(minutes).padStart(2, '0');
                if (secondsEl) secondsEl.textContent = String(seconds).padStart(2, '0');
            } else {
                if (countdownContainer) {
                    countdownContainer.innerHTML = `
                        <div class="col-span-4 text-center py-4 bg-emerald-500/20 border border-emerald-500/30 rounded-xl">
                            <span class="text-emerald-300 font-bold text-lg">Conference is currently live!</span>
                        </div>
                    `;
                }
            }
        };

        updateCountdown();
        setInterval(updateCountdown, 1000);
    }

    // 4. Abstract Submission Live Word Counter
    const abstractTextarea = document.getElementById('abstract_text');
    const wordCountDisplay = document.getElementById('word-count-display');
    const wordCountWarning = document.getElementById('word-count-warning');

    if (abstractTextarea && wordCountDisplay) {
        const checkWordCount = () => {
            const text = abstractTextarea.value.trim();
            const words = text ? text.split(/\s+/).length : 0;
            wordCountDisplay.textContent = words;

            if (words > 200) {
                wordCountDisplay.classList.remove('text-slate-500', 'text-emerald-600');
                wordCountDisplay.classList.add('text-rose-600', 'font-bold');
                if (wordCountWarning) wordCountWarning.classList.remove('hidden');
            } else {
                wordCountDisplay.classList.remove('text-rose-600');
                wordCountDisplay.classList.add('text-emerald-600');
                if (wordCountWarning) wordCountWarning.classList.add('hidden');
            }
        };

        abstractTextarea.addEventListener('input', checkWordCount);
        checkWordCount();
    }

    // 5. Dynamic Fee Calculator on Registration Page & Landing Widget
    const categorySelect = document.getElementById('reg_category');
    const feeDisplayAmount = document.getElementById('fee-display-amount');
    const feeDisplayCurrency = document.getElementById('fee-display-currency');
    const feeDisplayDesc = document.getElementById('fee-display-desc');

    if (categorySelect && feeDisplayAmount) {
        const updateFeeDetails = () => {
            const selectedOption = categorySelect.options[categorySelect.selectedIndex];
            const amount = selectedOption.getAttribute('data-amount');
            const currency = selectedOption.getAttribute('data-currency') || 'NGN';
            const symbol = selectedOption.getAttribute('data-symbol') || '₦';
            const desc = selectedOption.getAttribute('data-desc') || '';

            if (amount) {
                const formatted = Number(amount).toLocaleString();
                feeDisplayAmount.textContent = `${symbol}${formatted}`;
            } else {
                feeDisplayAmount.textContent = `${symbol}0`;
            }

            if (feeDisplayCurrency) feeDisplayCurrency.textContent = currency;
            if (feeDisplayDesc) feeDisplayDesc.textContent = desc;
        };

        categorySelect.addEventListener('change', updateFeeDetails);
        updateFeeDetails();
    }

    // 6. Subtheme Filter & Search
    const subthemeSearchInput = document.getElementById('subtheme-search');
    const subthemeItems = document.querySelectorAll('.subtheme-item');
    const trackSections = document.querySelectorAll('.track-section');

    if (subthemeSearchInput && subthemeItems.length > 0) {
        subthemeSearchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();

            subthemeItems.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(query)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });

            // Hide track section if no items inside are visible
            trackSections.forEach(section => {
                const visibleItems = section.querySelectorAll('.subtheme-item[style*="display: block"], .subtheme-item:not([style*="display: none"])');
                const hasVisible = Array.from(section.querySelectorAll('.subtheme-item')).some(it => it.style.display !== 'none');
                section.style.display = hasVisible ? 'block' : 'none';
            });
        });
    }

    // 7. Auto-dismiss Flash Alerts after 6 seconds
    const flashAlerts = document.querySelectorAll('.flash-alert');
    flashAlerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 500);
        }, 6000);
    });

    // 8. Copy to Clipboard Utility
    window.copyText = function(text, btnElement, successMsg = "Copied!") {
        navigator.clipboard.writeText(text).then(() => {
            if (btnElement) {
                const originalHtml = btnElement.innerHTML;
                btnElement.innerHTML = `<span class="text-xs text-emerald-600 font-semibold">${successMsg}</span>`;
                setTimeout(() => {
                    btnElement.innerHTML = originalHtml;
                }, 2000);
            }
        });
    };
});
