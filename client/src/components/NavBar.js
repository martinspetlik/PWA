import React, { Component } from 'react'
import { Link, withRouter } from 'react-router-dom'
import Navbar from 'react-bootstrap/Navbar'
import Nav from 'react-bootstrap/Nav'
import NavDropdown from 'react-bootstrap/NavDropdown'

import cookie from 'react-cookies'

class NavBar extends Component {

    createLink() {
        let path = "/chats"
        if (cookie.load("chats") === undefined) {
                        path = "/chats"
                    } else {
                        if (cookie.load("chats").length === 0) {
                             path = "/chats"
                        }
                        console.log("cookie.load(chats).length " + cookie.load("chats").length)
                        Object.keys(cookie.load("chats")).map(key => (
                             path = "/chat/" + cookie.load("chats")[key]["id"]
                        ))
                    }


        return (<Link to={path} className="nav-link">
                        Chats
               </Link>)
    }


    render () {
        const loginRegLink = (
            <ul className="navbar-nav">
                <li className="nav-item">
                    <Link to="/registration" className="nav-link">
                        Registration
                    </Link>
                </li>
            </ul>
        )

        const userLink = (
            <ul className="navbar-nav">
                <li className="nav-item">

                    {this.createLink()}


                </li>
                <li className="nav-item">
                    <Link to="/logout" className="nav-link">
                        Logout
                    </Link>
                </li>
            </ul>
        )

        return (
            <nav className="navbar fixed-top navbar-expand navbar-dark bg-dark">
                <div className="collapse navbar-collapse" id="navbarNav">
                    <ul className="navbar-nav">
                        <li className="nav-item">
                            <Link to="/" className="nav-link">
                                Home
                            </Link>
                        </li>
                    </ul>
                    {cookie.load('token') ? userLink : loginRegLink}
                </div>
            </nav>




        )
    }
}

export default withRouter(NavBar)