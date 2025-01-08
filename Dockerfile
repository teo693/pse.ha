ARG BUILD_FROM
FROM $BUILD_FROM

# Copy data for add-on
COPY pse.py /

CMD [ "python3 pse.py" ]
