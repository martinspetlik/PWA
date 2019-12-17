import React, { Component } from 'react'
import cookie from 'react-cookies';
import openSocket from 'socket.io-client'
import './chat.css';
import { confirmAlert } from 'react-confirm-alert'; // Import
import 'react-confirm-alert/src/react-confirm-alert.css';
import Avatar from 'react-avatar';
import {AlertDanger, AlertPrimary} from "./Alerts";
import NativeListener from 'react-native-listener';



class Chat extends Component {

    constructor() {
        super()


        this.state = {
            name: '',
            email: '',
            chats: '',
            messages: [],
            mes: '',
            chat_id: '',
            new_message: false,
            redirect: '',
            socket: openSocket('wss://pwachat2.herokuapp.com')

        }

        this.onChange = this.onChange.bind(this)
        this.onSubmit = this.onSubmit.bind(this)

        this.onSubmitAdd = this.onSubmitAdd.bind(this)
        this.onSubmitRemove = this.onSubmitRemove.bind(this)
        this.routeChange = this.routeChange.bind(this)

        this.state.socket.on("message", msg => {
            this.setState(messages => ({
                             messages: [...this.state.messages, msg]
            }))

            this.setState({new_message: true})
        })
    }

    onChange (e) {
        this.setState({ [e.target.name]: e.target.value })
    }

    onSubmitRemove(e) {
        e.preventDefault()

        confirmAlert({
              title: 'Confirm to submit',
              message: 'Are you sure to delete chat',
              buttons: [
                {
                  label: 'Yes',
                  onClick: () => this.deleteChat()
                },
                {
                  label: 'No',
                  onClick: () => {}
                }
              ]
        });

    }

    deleteChat() {

        fetch("/chat/" + this.state.chat_id, {
            method: 'DELETE',
        }).then(response => response.json())
            .then(res => {
                if (res.success) {
                    cookie.remove("chats", {path: "/"})
                    this.props.history.push("/chats")
                    window.location.reload()
                }
            });
    }

    onSubmitAdd(e) {
        e.preventDefault()
        this.props.history.push("/chats/add")
    }

    handleMessage() {
        // this.state.socket.send({'author': cookie.load('current_user_name'), 'text': this.state.mes},
        //         this.state.chat_id)

        this.state.socket.send({'author': cookie.load('current_user_name'), 'text': this.state.mes},
                this.state.chat_id)

    }

    onSubmit (e) {
        this.handleMessage()

        //e.preventDefault()
        //e.stopPropagation();


        //}

        //e.stopPropagation()
        //e.stopImmediatePropagation()
    }

    componentDidUpdate() {
         this.scrollToBottom();
    }

    componentDidMount(){
        if (cookie.load('token')) {

            fetch("/chats", {
                method: 'GET',
                headers: new Headers({
                    Authorization: 'Bearer ' + cookie.load('token')
                }),
            })
                .then(response => response.json())
                .then(resData => {
                    cookie.save("chats", resData, {path: "/"});
                })
        }

        if (cookie.load('token')) {

            var path = this.props.location.pathname.split("/")
            var chat_id = path[path.length-1]

            this.state.chat_id = chat_id

            this.state.socket.emit("join", {
                'username': cookie.load('current_user_name'),
                'room': chat_id
            })

            this.state.socket.emit("load_messages", this.state.chat_id)
            this.state.socket.on("all_messages", messages => {
                if (messages[0] === false) {
                    this.props.history.push("/chats")
                }

                this.setState({messages: messages});
            })

            this.state.name = cookie.load('current_user_name')
            this.state.chats = cookie.load("chats")
        }

        this.scrollToBottom();
    }

    createContacts(){
        let contacts = []
        for (let key in this.state.chats) {
            let divStyle = {}
            let title = this.state.chats[key].members
            if (this.state.chat_id === this.state.chats[key].id) {
                divStyle = {backgroundColor: "#3E8477"}
            }

            if (this.state.chats[key].title !== "") {
                title = this.state.chats[key].title
            }

            contacts.push(
                <li className="contact"
                    onClick={this.routeChange}
                    id={this.state.chats[key].id}
                    style={divStyle}
                >

                    <div className="wrap">
                        <span className="contact-status offline"></span>
                        <Avatar name={title} className="avatar" size="40px"/>
                        <div className="meta">
                            <p>{title}</p>
                        </div>
                    </div>
                </li>
            )
        }
        return contacts
    }

    createMessages(){
        let messages = []
        for (let key in this.state.messages) {
            let status = {}
            if (this.state.name === this.state.messages[key][0]) {
                status = "sent"
            } else {
                status = "replies"
            }

            messages.push(
                <li className={status}>
                         <Avatar name={this.state.messages[key][0]} className="avatar" size="30px"/>
                         <p>{this.state.messages[key][1]}</p>
                </li>
            )
        }
        return messages
    }

    routeChange(e) {
        const key = e.currentTarget.id
        if (this.state.chat_id !== key) {
            this.props.history.push("/chat/" + key)
            window.location.reload()
        }
    }

    scrollToBottom = () => {
            this.messagesEnd.scrollIntoView({ behavior: "smooth" });
    }




    render () {

        return (
            <div id="frame">
                <div id="sidepanel">
                    <div id="profile">
                        <div className="wrap">
                            <Avatar name={this.state.name} className="avatar" size="50px"/>
                            <p>{this.state.name}</p>
                        </div>
                    </div>
                    <div id="contacts">
                        <ul>
                            {this.createContacts()}

                        </ul>
                    </div>
                    <div id="bottom-bar">
                        <form onSubmit={this.onSubmitAdd}>
                        <button id="addcontact" ><i className="fa fa-plus-square fa-fw" aria-hidden="true"></i> <span>Add chat</span>
                        </button>
                        </form>
                        <form onSubmit={this.onSubmitRemove}>
                        <button id="settings"><i className="fa fa-minus-square fa-fw" aria-hidden="true"></i>
                            <span>Remove chat</span></button>
                        </form>

                    </div>
                </div>
                <div className="content">
                    <div className="messages">
                        <ul id="all_messages">
                            {this.createMessages()}
                        </ul>
                        <div style={{ float:"left", clear: "both" }}
                            ref={(el) => { this.messagesEnd = el; }}>
                        </div>
                    </div>

                    <div className="message-input">
                        <div className="wrap">
                             <form onSubmit={(e) => this.onSubmit(e)}>
                                <input type="text"
                                       name="mes"
                                       value={this.state.mes}
                                       onChange={this.onChange}
                                       placeholder="Write your message..."/>
                            <button className="submit"><i className="fa fa-paper-plane" aria-hidden="true"></i></button>
                             </form>
                             </div>
                    </div>
                </div>
            </div>


        )

    }




}

export default Chat