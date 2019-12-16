import {Component} from "react";
import cookie from "react-cookies";
import React from "react";

import Select from 'react-select'
import io from "socket.io-client";
import {AlertDanger, AlertPrimary} from "./Alerts";


class ChatAdd extends Component {
    constructor() {
        super()

       this.state = {
            users: [],
            title: '',
            members: []
        }

        this.onChange = this.onChange.bind(this)
        this.onSubmit = this.onSubmit.bind(this)
    }

    onChange (e) {
        this.setState({ [e.target.name]: e.target.value })

    }


    handleChange = (selectedOption) => {
          this.setState({ members:selectedOption });
    }


    onSubmit (e) {
        e.preventDefault()

        fetch("/chats/add", {
            method: 'POST',
            // mode: 'no-cors',
            headers: new Headers({
                    Authorization: 'Bearer ' + cookie.load('token'),
                'Content-Type': 'application/json'}),
            body: JSON.stringify({
                    title: this.state.title,
                    members: this.state.members
		 	}),

        })
        .then(response => response.json())
        .then(res => {
            if (res.success) {
                this.setState({ message: AlertPrimary(res.message) });
                // setTimeout(function () {
                //     console.log('after');
                // }, 3000);
                let chats =  [...cookie.load("chats"), res.chat]

                cookie.save("chats", chats, {path: "/"})

                this.props.history.push("/chat/" + res.chat.id)

            } else {
                this.setState({ message: AlertDanger(res.message) });
            }

        });

    }

    componentDidMount() {
        fetch("/chats/add", {
            method: 'GET',
            mode: 'no-cors',
            headers: new Headers({
                    Authorization: 'Bearer ' + cookie.load('token')
                }),
        })
        .then(response => response.json())
        .then(resData => {
            this.state.users = resData
            this.setState({ users: resData});

        })
    }


    render () {

        const users = this.state.users

        return (
            <div className="container">
                <div className="row">
                    <div className="col-md-6 mt-5 mx-auto">

                        {this.state.message}

                    <form noValidate onSubmit={this.onSubmit}>
                        <div className="form-group">
                        <input type="text"
                               name="title"
                               className="form-control"
                               placeholder="Enter chat title"
                               maxlength="25"
                               value={this.state.title}
                               onChange={this.onChange}
                        />
                        </div>
                        <div className="form-group">
                              <Select
                                //defaultValue={[colourOptions[2], colourOptions[3]]}
                                isMulti
                                name="members"
                                options={users}
                                className="basic-multi-select"
                                classNamePrefix="select user"
                                onChange={this.handleChange}
                                // value={this.state.members}
                              />
                        </div>
                    <button type="submit" className="btn btn-lg btn-primary btn-block">
                                        Create
                    </button>
                    </form>
                    </div>
                </div>
            </div>

        )
    }
}
export default ChatAdd