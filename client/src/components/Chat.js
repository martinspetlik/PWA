import React, { Component } from 'react'
import cookie from 'react-cookies';
import io from 'socket.io-client'
import './chat.css';

import { Redirect } from 'react-router-dom'
import Avatar from 'react-avatar';


const socket = io('/')

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
            redirect: ''

        }

        this.onChange = this.onChange.bind(this)
        this.onSubmit = this.onSubmit.bind(this)

        this.onSubmitAdd = this.onSubmitAdd.bind(this)
        this.routeChange = this.routeChange.bind(this)
    }

    onChange (e) {
        this.setState({ [e.target.name]: e.target.value })
    }


    onSubmitAdd(e) {
        e.preventDefault()

        this.props.history.push("/chats/add")
    }

    onSubmit (e) {
        e.preventDefault()

        //var socket = this.state.socket

        var new_message = false;

        //console.log(this.state.chat_id)

        socket.send({'author': cookie.load('current_user_name'), 'text': this.state.mes},
            this.state.chat_id)

        //console.log("MESSAGES " + this.state.messages)

        socket.on("message", msg => {
            //console.log("New message " + msg)
            this.setState(messages => ({
                             messages: [...this.state.messages, msg]
            }))

            new_message = true
        })
    }

    componentDidMount(){

        //console.log("CHAT cookie token " + cookie.load('token'))
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

            //console.log("cookie chats " + cookie.load("chats"))
        }

        if (cookie.load('token')) {

            var path = this.props.location.pathname.split("/")
            var chat_id = path[path.length-1]

            this.state.chat_id = chat_id

            socket.emit("join", {
                'username': cookie.load('current_user_name'),
                'room': chat_id
            })

            socket.emit("load_messages", this.state.chat_id)
            socket.on("all_messages", messages => {
                //console.log("ALL messages " + messages)
                //console.log("delka " + messages.length)
                this.setState({messages: messages});
                //console.log("Socket this state messages " + this.state.messages)
            })

            //console.log("this.state.messages " + this.state.messages)


            this.state.name = cookie.load('current_user_name')
            this.state.chats = cookie.load("chats")

            //console.log(this.state.messages)
            //console.log("MESSAGES")
           // console.log(this.state.chats)
        }
    }

    createContacts(){
        let contacts = []
        for (let key in this.state.chats) {
            let divStyle = {}
            if (this.state.chat_id === this.state.chats[key].id) {
                divStyle = {backgroundColor: "#3E8477"}
            }

            contacts.push(
                <li className="contact"
                    onClick={this.routeChange}
                    id={this.state.chats[key].id}
                    style={divStyle}
                >

                    <div className="wrap">
                        <span className="contact-status offline"></span>
                        <Avatar name={this.state.chats[key].members} className="avatar" size="40px"/>
                        <div className="meta">
                            <p>{this.state.chats[key].members}</p>
                        </div>
                    </div>
                </li>
            )
        }
        return contacts
    }

    routeChange(e) {
        const key = e.currentTarget.id
        if (this.state.chat_id !== key) {
            this.props.history.push("/chat/" + key)
            window.location.reload()
        }
    }

    render () {
        const messages = (
            this.state.messages.map((message) =>
                <li className={message[3]}>
                         <Avatar name={message[0]} className="avatar" size="30px"/>
                         <p>{message[1]}</p>
                </li>

        ))

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
                        <button id="addcontact" ><i className="fa fa-user-plus fa-fw" aria-hidden="true"></i> <span>Add chat</span>
                        </button>
                        </form>
                    </div>
                </div>
                <div className="content">
                    <div className="messages">
                        <ul id="all_messages">
                            {messages}
                        </ul>
                    </div>

                    <div className="message-input">
                        <div className="wrap">
                             <form onSubmit={this.onSubmit}>
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