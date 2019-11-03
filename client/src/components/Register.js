import React, { Component } from 'react'
import { register } from './UserFunctions'
import { AlertDanger, AlertPrimary } from './Alerts'

import Alert from 'react-bootstrap/Alert'

class Register extends Component {
    constructor() {
        super()
        this.state = {
            name: '',
            email: '',
            password: '',
            message: ''
        }

        this.onChange = this.onChange.bind(this)
        this.onSubmit = this.onSubmit.bind(this)
    }

    onChange (e) {
        this.setState({ [e.target.name]: e.target.value })
    }

    onSubmit (e) {
        e.preventDefault()

        const newUser = {
            name: this.state.name,
            email: this.state.email,
            password: this.state.password
        }

        register(newUser).then(res => {
            //console.log(res.success)
            //console.log(res.message)
            if(!res.success) {
                this.setState({ message: AlertDanger(res.message) });
            } else {
                //this.state.message = AlertPrimary(res.message)
                this.props.history.push(`/`)
            }


            console.log(this.message)

        })
    }

    render () {
        return (
            <div className="container">
                <div className="row">
                    <div className="col-md-6 mt-5 mx-auto">

                        {this.state.message}

                        <form onSubmit={this.onSubmit}>

                            <h1 className="h3 mb-3 font-weight-normal">Registration</h1>
                            <div className="form-group">
                                <label htmlFor="name">User Name</label>
                                <input type="text"
                                    className="form-control"
                                    name="name"
                                    placeholder="Enter User name"
                                    value={this.state.name}
                                    onChange={this.onChange}
                                    required/>
                            </div>

                            <div className="form-group">
                                <label htmlFor="email">Email Address</label>
                                <input type="email"
                                    className="form-control"
                                    name="email"
                                    placeholder="Enter Email"
                                    value={this.state.email}
                                    onChange={this.onChange}
                                    required />
                            </div>
                            <div className="form-group">
                                <label htmlFor="password">Password </label>
                                <input type="password"
                                    className="form-control"
                                    name="password"
                                    placeholder="Enter Password"
                                    value={this.state.password}
                                    onChange={this.onChange}
                                    required />
                            </div>

                            <button type="submit" className="btn btn-lg btn-primary btn-block">
                                Register
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        )
    }
}

export default Register