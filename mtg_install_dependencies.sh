# Main information
echo "MTG Simulator: installing dependencies"
echo ""
# echo "It is highly recommend you use a recent Linux operating system (e.g., Ubuntu 20 or higher)."
echo "Python version 3.7+ is required."
echo ""

# General
sudo apt-get update || exit 1

pip install gurobipy || exit 1

pip install numpy || exit 1

pip install pandas || exit 1

echo ""
echo "MTG dependencies have been installed."
