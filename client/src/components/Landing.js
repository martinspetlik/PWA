import React, { Component } from 'react'
import Button from 'react-bootstrap/Button'
import Alert from 'react-bootstrap/Alert'

class Landing extends Component {
    render () {
        return (
            <div className="container">
                <div className="jumbotron mt-5">
                    <div className="col-sm-8 mx-auto">
                        <h1 className="text-center">Welcome to chat application</h1>
                    </div>
                </div>
            </div>
        )
    }
}




export default Landing