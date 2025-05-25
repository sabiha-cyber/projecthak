import streamlit as st
from web3 import Web3

def app():
    # --- Configurations ---
    INFURA_PROJECT_ID = "340c624898824c09a1c6a98c8b8079bb"
    INFURA_URL = f"https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}"

    web3 = Web3(Web3.HTTPProvider(INFURA_URL))

    st.title("Simple Blockchain Feature Demo")

    if web3.is_connected():
        st.success("Connected to Ethereum Goerli Testnet")
    else:
        st.error("Failed to connect to Ethereum")

    # Input Ethereum address to check balance
    r_address = st.text_input("Enter Ethereum address to check balance")
    address = Web3.to_checksum_address("0x5B38Da6a701c568545dCfcB03FcB875f56beddC4")

    if address:
        if web3.is_address(address):
            balance = web3.eth.get_balance(address)
            st.write(f"Balance : {Web3.from_wei(balance, 'ether')} ETH")
        else:
            st.error("Invalid Ethereum address")

    st.markdown("---")

    # Send ETH section
    st.subheader("Send ETH Transaction (Goerli Testnet)")

    private_key = st.text_input("Your Private Key (for demo only!)", type="password")
    recipient = st.text_input("Recipient Address")
    amount = st.number_input("Amount in ETH", min_value=0.0001, step=0.0001, format="%.4f")

    if st.button("Send Transaction"):
        if not web3.is_address(recipient):
            st.error("Invalid recipient address")
        elif not private_key:
            st.error("Private key is required")
        else:
            try:
                account = web3.eth.account.from_key(private_key)
                nonce = web3.eth.get_transaction_count(account.address)

                tx = {
                    'nonce': nonce,
                    'to': Web3.to_checksum_address(recipient),
                    'value': web3.to_wei(amount, 'ether'),
                    'gas': 21000,
                    'gasPrice': web3.to_wei('50', 'gwei')
                }


                signed_tx = account.sign_transaction(tx)
                tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                st.success(f"Transaction sent! Hash: {web3.toHex(tx_hash)}")
            except Exception as e:
                st.error(f"Error sending transaction: {str(e)}")
