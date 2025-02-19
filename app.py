from app_factory import create_app

app = create_app(config_name="DEVELOPMENT")
app.app_context().push()

if __name__ == "__main__":
    app.run(debug=True, port=8022)
