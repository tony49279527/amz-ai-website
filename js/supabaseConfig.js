const SUPABASE_URL = 'YOUR_SUPABASE_URL_HERE';
const SUPABASE_ANON_KEY = 'YOUR_SUPABASE_ANON_KEY_HERE';
const PAYPAL_PAYMENT_URL = 'https://www.paypal.com/ncp/payment/2Z7UB3AXAUQYG';
const N8N_PAYMENT_WEBHOOK_URL = 'YOUR_N8N_WEBHOOK_URL_HERE';

// Initialize Supabase client if library is loaded
let supabaseClient = null;
if (typeof supabase !== 'undefined') {
    supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
} else {
    console.warn('Supabase library not loaded');
}
