echo '#!/bin/bash' > start.sh
echo 'gunicorn -w 4 -b 0.0.0.0:8000 run:app' >> start.sh
chmod +x start.sh  # Cấp quyền thực thi
