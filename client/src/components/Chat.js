import React, { Component } from 'react'
import cookie from 'react-cookies';
import io from 'socket.io-client'
import './chat.css';

import { Redirect } from 'react-router-dom'
import Avatar from 'react-avatar';

const socket = io('http://localhost:5000')

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
            new_message: false

        }

        this.onChange = this.onChange.bind(this)
        this.onSubmit = this.onSubmit.bind(this)
    }

    onChange (e) {
        this.setState({ [e.target.name]: e.target.value })
    }

    onSubmit (e) {
        e.preventDefault()

        var new_message = false;

        console.log(this.state.chat_id)

        socket.send({'author': cookie.load('current_user_name'), 'text': this.state.mes},
            this.state.chat_id)

        console.log("MESSAGES " + this.state.messages)

        socket.on("message", msg => {
            console.log("New message " + msg)
            this.setState(messages => ({
                             messages: [...this.state.messages, msg]
            }))

            new_message = true
        })
    }

    // loadMessages() {
    //     socket.emit("load_messages", this.state.chat_id)
    //     socket.on("all_messages", messages => {
    //         console.log("ALL messages " + messages)
    //         console.log("delka " + messages.length)
    //         this.setState({messages: messages});
    //     })

        // console.log("delka " + messages.length)



        // fetch(this.props.location.pathname, {
        //         method: 'GET',
        //         headers: new Headers({
        //             Authorization: 'Bearer ' + cookie.load('token')
        //         }),
        //     })
        //         .then(response => response.json())
        //         .then(resData => {
        //             console.log(resData)
        //             console.log(typeof resData)
        //             // var result = JSON.parse(resData);
        //             //
        //             // console.log(result)
        //             // console.log(typeof result)
        //             this.setState({messages: resData});
        //             // console.log(typeof this.state.chats)
        //             // console.log(this.state.chats)
        //
        //             // var chats_array = []
        //             // for (var key of Object.keys(this.state.chats)) {
        //             //     chats_array =
        //             //     console.log(key + " -> " + this.state.chats[key].members)
        //             //     }
        //         })
    //}


    componentDidMount(){
        if (cookie.load('token')) {

            var path = this.props.location.pathname.split("/")
            var chat_id = path[path.length-1]

            this.state.chat_id = chat_id

            // socket.on("connect", function() {
            //     socket.send("User connected")
            // })

            socket.emit("join", {'username': cookie.load('current_user_name'),
                'room': chat_id})

            socket.emit("load_messages", this.state.chat_id)
            socket.on("all_messages", messages => {
                console.log("ALL messages " + messages)
                console.log("delka " + messages.length)
                this.setState({messages: messages});
                console.log("Socket this state messages " + this.state.messages)
            })

            setTimeout(function(){
                console.log('after');
            },500);

            //this.loadMessages()

            console.log("this.state.messages " + this.state.messages)

        //      for (var i = 0; i < this.state.messages.length; i++) {
        //     console.log(JSON.stringify(this.state.messages[i]))
        // }

            //this.setSocketListeners()

            this.state.name = cookie.load('current_user_name')
            this.state.chats = cookie.load("chats")

            console.log(this.state.messages)
            console.log("MESSAGES")
            console.log(this.state.chats)
        }
    }

    routeChange(key) {
        var path = this.props.location.pathname.split("/")
        console.log("path " + path[path.length-1])
        if (path[path.length -1] !== key) {
            return <Redirect to='http://localhost:3000/chats/{key}'/>
        }
    }


    render () {

        const contacts = (

        Object.keys(this.state.chats).map(key => (
                <li className="contact">
                    <div className="wrap" onClick={this.routeChange(key)}>
                        <span className="contact-status offline"></span>
                        <Avatar name={this.state.chats[key].members} className="avatar" size="40px"/>
                        <div className="meta">
                            <p>{this.state.chats[key].members}</p>
                        </div>
                    </div>
                </li>
        )
            )
        )

        const messages = (
            this.state.messages.map((message) =>
                <li className={message[3]}>
                         <Avatar name={message[0]} className="avatar" size="30px"/>
                         <p>{message[1]}</p>
                </li>

        ))

        // const messages = (
        //     Object.keys(this.state.messages).map(key => (
        //             <li className={this.state.messages[key].status}>
        //                 <Avatar name={this.state.name} className="avatar" size="30px"/>
        //                 <p>{this.state.messages[key].text}</p>
        //             </li>
        //     )
        //         )
        // )

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
                            {contacts}
                        </ul>
                    </div>
                    <div id="bottom-bar">
                        <button id="addcontact"><i className="fa fa-user-plus fa-fw" aria-hidden="true"></i> <span>Add contact</span>
                        </button>
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