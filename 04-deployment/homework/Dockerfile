FROM agrigorev/zoomcamp-model:mlops-2024-3.10.13-slim

WORKDIR /app

COPY homework.py homework.py
COPY Pipfile* ./

# install dependencies based on Pipfile
RUN pip install pipenv && pipenv install --system

# Default command (can be overridden)
ENTRYPOINT [ "python", "homework.py" ]
CMD [ "--year", "2023", "--month", "5"]