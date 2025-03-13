echo '#!/bin/bash' > start.sh
echo 'gunicorn -w 4 -b 0.0.0.0:$PORT run:app' >> start.sh
pip install pinecone-client==2.2.1
chmod +x start.sh  # Cấp quyền thực thi
