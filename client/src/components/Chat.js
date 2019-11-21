import React, { Component } from 'react'
import cookie from 'react-cookies';
import io from 'socketio-jwt';
import 'socketio-jwt';
import './chat.css';

import { Redirect } from 'react-router-dom'

import {Link} from "react-router-dom";
import { AlertDanger, AlertPrimary } from './Alerts'
import Avatar from 'react-avatar';
import {login} from "./UserFunctions";

class Chat extends Component {

    constructor() {
        super()

        this.state = {
            name: '',
            email: '',
            chats: '',
            messages: '',
            mes: ''

        }

        this.onChange = this.onChange.bind(this)
        this.onSubmit = this.onSubmit.bind(this)
    }

    onChange (e) {
        this.setState({ [e.target.name]: e.target.value })
    }

    onSubmit (e) {
        // io = require('socket.io-client')();

        var io            = require("socket.io-client")('http://localhost:3000/message/');
        e.preventDefault()

        console.log("on submit")

        // var socket = io.connect('http://localhost:9000');
        // socket.on('connect', function (socket) {
        //     socket
        //     .on('authenticated', function () {
        //         //do other things
        //         })
        //     .emit('authenticate', {token: cookie.load('token')}); //send the jwt
        //     });

        const socket = io.connect('http://localhost:3000/message');
            socket.on('connect', () => {
              socket
                .emit('authenticate', { token: cookie.load('token')}) //send the jwt
                .on('authenticated', () => {
                  //do other things
                })
                .on('unauthorized', (msg) => {
                  console.log(`unauthorized: ${JSON.stringify(msg.data)}`);
                  throw new Error(msg.data.type);
                })
            });

        // io.sockets
        //     .on('connection', socketioJwt.authorize({
        //         secret: cookie.load('token'),
        //         timeout: 15000 // 15 seconds to send the authentication message
        //     })).on('authenticated', function(socket) {
        //         //this socket is authenticated, we are good to handle more events from it.
        //         console.log('hello! ' + socket.decoded_token.name);
        //     });




        const message = {
            mes: this.state.mes,
        }
        //const [cookies, setCookie] = useCookies(['chat']);

    }


    componentDidMount(){
        //console.log(cookie.load('token'))
        if (cookie.load('token')) {

            fetch(this.props.location.pathname, {
                method: 'GET',
                headers: new Headers({
                    Authorization: 'Bearer ' + cookie.load('token')
                }),
            })
                .then(response => response.json())
                .then(resData => {
                    console.log(resData)
                    console.log(typeof resData)
                    // var result = JSON.parse(resData);
                    //
                    // console.log(result)
                    // console.log(typeof result)
                    this.setState({messages: resData});
                    // console.log(typeof this.state.chats)
                    // console.log(this.state.chats)

                    // var chats_array = []
                    // for (var key of Object.keys(this.state.chats)) {
                    //     chats_array =
                    //     console.log(key + " -> " + this.state.chats[key].members)
                    //     }
                })

            this.state.name = cookie.load('current_user_name')

            this.state.chats = cookie.load("chats")



            // Object.keys(this.state.chats).map(key => (
            //    console.log(key)
            //     // this.routeChange(key)
            // ))

            console.log(this.state.messages)
            console.log("MESSAGES")
            console.log(this.state.chats)
        }
    }

    routeChange(key) {
        console.log("key " + key)
        // console.log(typeof key)
        // console.log(this.props.location.pathname)
        // console.log(this.props.location.pathname.split("/"))

        var path = this.props.location.pathname.split("/")

        console.log("path " + path[path.length-1])
        // console.log(typeof path[path.length-1])

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

        Object.keys(this.state.messages).map(key => (
                <li className={this.state.messages[key].status}>
                    <Avatar name={this.state.name} className="avatar" size="30px"/>
                    <p>{this.state.messages[key].text}</p>
                </li>
        )
            )
        )

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