from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
a = check_password_hash('scrypt:32768:8:1$myXboKBF5cT8Qcpu$5c9df842336ddca92c07262f48dec68f139fe2cf3df29946ba5d83ca0e43b8141ac887dd085be9bd2c66368cf5b42faed932d0fffbbb2ed5dc46b071e81b2237','us1234')
print(a)

"""b = generate_password_hash('us1234')
print(b)

c = check_password_hash(b,'us1234')
print(c)"""

