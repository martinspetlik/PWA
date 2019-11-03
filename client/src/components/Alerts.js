import React from 'react'
import Button from 'react-bootstrap/Button'
import Alert from 'react-bootstrap/Alert'

export const AlertPrimary = (message)=> {

    return (
      <Alert variant="primary">
        <p>
            {message}
        </p>
      </Alert>
    );
}


export const AlertDanger= (message)=> {
    return (
      <Alert variant="danger">
        <p>
            {message}
        </p>
      </Alert>
    );
}

