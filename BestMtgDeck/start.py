import os

from flask import Flask

from BestMtgDeck.routes import main


def create_app(config_class=None):
    flask_app = Flask(__name__)  # initialize website
    if config_class:
        flask_app.config.from_object(config_class)
    else:
        # cryptography for cookie used as key of stored collections dict
        flask_app.secret_key = os.getenv(
            "SECRET KEY", b":\xafq\x87\xe0\x12\xbfU\xeeC\x9b\x17\xcfs\xaf)"
        )
        flask_app.config["PAYPAL_LINK"] = os.getenv("PAYPAL_LINK", None)

    flask_app.register_blueprint(main)
    return flask_app


app = create_app(None)


if __name__ == "__main__":
    app.run(debug=True)
