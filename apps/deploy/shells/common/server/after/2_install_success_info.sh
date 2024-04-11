

echo "Installation successful."

tmp_config="/tmp/deploy.env"

if [ -f "$tmp_config" ]; then
    echo "Reading installation configuration from $tmp_config..."
    source $tmp_config

    for key in $(grep -oP '^\w+' $tmp_config); do
        value="${!key}"
        echo "$key: $value"
    done
else
    echo "Installation successful , Configuration file not found."
fi
