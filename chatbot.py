import openai
import streamlit as st

def app():
    st.title("Chat Bot")

    openai.api_key = "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"
    openai.base_url = "https://api.groq.com/openai/v1/"  

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "llama3-70b-8192"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            stream = openai.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)

        st.session_state.messages.append({"role": "assistant", "content": response})


def price_advice(item :str) -> str:
    openai.api_key = "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"
    openai.base_url = "https://api.groq.com/openai/v1/"  

    prompt = f"What is a fair market price for {item}.Reply in a single word in USD?"

    response = openai.chat.completions.create(
                model= "llama3-70b-8192",
                messages=[
                    {"role": "user", "content": prompt}
                ]
    )
    return response.choices[0].message.content.strip()


    


    
