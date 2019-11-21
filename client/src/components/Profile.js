import React, { Component } from 'react'
import cookie from 'react-cookies';
import { AlertDanger, AlertPrimary } from './Alerts'

class Profile extends Component {
    constructor() {
        super()
        this.state = {
            name: '',
            email: ''
        }
    }

    componentDidMount(){
        console.log(cookie.load('token'))
        if (cookie.load('token')) {

            fetch("http://localhost:3000/profile", {
                method: 'GET',
                headers: new Headers({
                    Authorization: 'Bearer ' + cookie.load('token')
                }),
            })
                .then(response => response.json())
                .then(resData => {
                    console.log(JSON.stringify(resData))
                    this.setState({name: resData.name, email: resData.email});
                })
        }
    }


    render () {

        const notLogin = (
            AlertDanger("You are not loged in!")
        )

        const isLogin = (
            <div className="container">
                <div className="jumbotron mt-5">
                    <div className="col-sm-8 mx-auto">
                        <h1 className="text-center">PROFILE</h1>
                    </div>
                    <table className="table col-md-6 mx-auto">
                        <tbody>
                            <tr>
                                <td>First Name</td>
                                <td>{this.state.name}</td>
                            </tr>
                            <tr>
                                <td>Email</td>
                                <td>{this.state.email}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        )


        return (
            cookie.load('token') ? isLogin : notLogin
        )
    }
}

export default Profile