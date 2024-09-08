<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بوت رصيد الإنترنت</title>
    <script>
        async function sendPhoneNumber() {
            const num = document.getElementById('phone-number').value;
            const response = await fetch('/send_phone_number', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({num})
            });
            const result = await response.json();
            alert(result.message);
        }

        async function sendOtp() {
            const otp = document.getElementById('otp').value;
            const response = await fetch('/send_otp', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({otp})
            });
            const result = await response.json();
            alert(result.message);
        }

        async function checkBalance() {
            const response = await fetch('/check_balance');
            const result = await response.json();
            alert(`رصيدك: ${result.balance}\nتاريخ الصلاحية: ${result.expiry_date}`);
        }
    </script>
</head>
<body>
    <h1>بوت رصيد الإنترنت</h1>
    <label for="phone-number">رقم الهاتف:</label>
    <input type="text" id="phone-number">
    <button onclick="sendPhoneNumber()">إرسال رقم الهاتف</button>
    <br><br>
    <label for="otp">رمز التحقق:</label>
    <input type="text" id="otp">
    <button onclick="sendOtp()">إرسال رمز التحقق</button>
    <br><br>
    <button onclick="checkBalance()">استعلام عن الرصيد</button>
</body>
</html>
