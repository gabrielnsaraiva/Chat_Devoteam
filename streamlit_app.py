import os
import streamlit as st
from streamlit_float import *
from streamlit_feedback import streamlit_feedback
from streamlit_theme import st_theme
from streamlit_extras.stylable_container import stylable_container

import toml
#======================================================================================================================================
def create_index():
    chroma_client = chromadb.PersistentClient(path = db_path)
    
    collection = chroma_client.get_or_create_collection(name = colection_name)
    service_context = ServiceContext.from_defaults(embed_model = embed_model,
                                                   llm = llm,
                                                   chunk_size = 128, chunk_overlap = 50)
    
    vector_store = ChromaVectorStore(chroma_collection = collection )
    storage_context = StorageContext.from_defaults(vector_store = vector_store)
    
    index = VectorStoreIndex.from_vector_store( vector_store = vector_store,
                                                storage_context = storage_context,
                                                service_context = service_context
                                              )

    return index
#======================================================================================================================================
def initialize_session_state():
    
    
        
    if "history" not in st.session_state:
        st.session_state.history = []
   
    if "conversation" not in st.session_state:
        #*** ============================================================= ***
        # Add chat engine here
        #*** ============================================================= ***
        #llm = OpenAI(
        #    temperature=0,
        #    openai_api_key=st.secrets["openai_api_key"],
        #    model_name="text-davinci-003"
        #)
        #st.session_state.conversation = ConversationChain(
        #    llm=llm,
        #    memory=ConversationSummaryMemory(llm=llm),
        #)
        st.session_state.conversation = None
        pass

    if "feedback" not in st.session_state:
        st.session_state["feedback"] = None
        
    if len(st.session_state.history) == 0:
        st.session_state.history.append(
            {"role": "ai", "content": "Faz-me uma pergunta sobre a Devoteam"}    
        )
        
    if "chats" not in st.session_state:
        st.session_state.chats = []
        st.session_state.chat_number = 0
        st.session_state.chats.append(st.session_state.history)
            
        
def on_click_callback():
    if st.session_state.human_prompt == None:
        human_prompt = st.session_state.question_prompt
    else:
        human_prompt = st.session_state.human_prompt
    
    
    #llm_response = st.session_state.conversation.run(
    #    human_prompt
    #)

    llm_response = "Resposta Aqui!"
    st.session_state.history.append(
        {"role": "human", "content": human_prompt}
    )
    st.session_state.history.append(
        {"role": "ai", "content": llm_response}
    )

    st.session_state.chats[st.session_state.chat_number] = st.session_state.history

def chat_click(*args):
    chat_number = ""
    for val in args:
        chat_number += val
    
    chat_number = int(chat_number) - 1

    st.session_state.chat_number = chat_number
    st.session_state.history = st.session_state.chats[chat_number]

def new_chat():

    # save last chat
    st.session_state.chats[st.session_state.chat_number] = st.session_state.history
    
    # create new chat
    st.session_state.history = []
    st.session_state.chats.append(st.session_state.history)
    st.session_state.chat_number = len(st.session_state.chats) - 1

def drop_chat(*args):
    
    chat_number = ""
    for val in args:
        chat_number += val
    
    chat_number = int(chat_number) - 1

    if chat_number == st.session_state.chat_number: # remove the current chat
        st.session_state.chats.pop(st.session_state.chat_number)
        
        if len( st.session_state.chats) > 0: # tem mais chats available
            st.session_state.chat_number = 0 # the chat becomes the first one
            st.session_state.history = st.session_state.chats[0]
        else:
            new_chat()
    else:
        st.session_state.chats.pop(chat_number)
        if chat_number < st.session_state.chat_number:
            st.session_state.chat_number += -1
        

#======================================================================================================================================
def main():
        
    initialize_session_state()   
    with open("./style.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

    #================================================================================================================================================================================================
    #=== Header
    
    #================================================================================================================================================================================================
    # Divide in two columns
    col1, col2 = st.columns([1, 4])

    # First column -> Questions
    with col1:
              
        st.button(    "New Chat",
                      on_click = new_chat,
                 )
        # create a container for each chat
        container_chats = st.container(height = 300)
        with container_chats:
            cols = []
            num_chat = 1
            for chat in st.session_state.chats:
                col1_chat, col2_chat = st.columns([4, 1])
                cols.append([col1_chat, col2_chat])

                if chat[0]["role"] == "human":
                    first_message = chat[0]["content"]
                else:
                    try:
                        first_message = chat[1]["content"]
                    except:
                        first_message = "New Chat " + str(num_chat)

                with cols[num_chat - 1][0]:
                    st.button(first_message,
                              on_click = chat_click,
                              args = (str(num_chat)),
                              key = "btn_chat_" + str(num_chat)
                             )

                with cols[num_chat - 1][1]:
                    st.button("D",
                              on_click = drop_chat,
                              args = (str(num_chat)),
                              key = "btn_del_" + str(num_chat)
                             )
                st.divider()
                num_chat += 1
                
    with col2:
        
        chat_placeholder = st.container(height = 300, border = True)
        prompt_placeholder = st.container()
        container_devoteam = st.container()
    
        
        
        with chat_placeholder:
            for chat in st.session_state.history:
                div = f"""
                            <div class="chat-row 
                                {'' if chat["role"] == 'ai' else 'row-reverse'}">
                                <img class="chat-icon" src="{
                                    'https://pbs.twimg.com/profile_images/1082991650794889217/h4Bo8Z5E_400x400.jpg' if chat["role"] == 'ai' 
                                                  else 'https://cdn-icons-png.freepik.com/512/8428/8428718.png'}"
                                     width=40 height=40>
                                <div class="chat-bubble
                                {'ai-bubble' if chat["role"] == 'ai' else 'human-bubble'}">
                                    &#8203;{chat["content"]}
                                </div>
                            </div>
                    """
                st.markdown(div, unsafe_allow_html=True)
            
            for _ in range(3):
                st.markdown("")
        
        with prompt_placeholder:
            st.chat_input(
                "Chat Here!",
                on_submit = on_click_callback,
                key="human_prompt",
            )
            
        with container_devoteam:
            div = """
          <div style="display: flex; align-items: center; justify-content: flex-end; height: 70px;">
              <span style="color: #3c3c3a; margin-right: 0px; font-size: 2vh; font-weight: bold;">Powered by</span>
              <a href="https://pt.devoteam.com/pt-pt/" target="_blank">
                  <img src="https://storage.googleapis.com/gc-poc-cnn-ai-dev/sandbox-experimentation-gsaraiva/Randstad/Copy%20of%20devoteam_rgb.png" style="height: 60px;">
              </a>
          </div>
          """
            st.markdown(div, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
