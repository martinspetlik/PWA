import axios from 'axios'

export const register = newUser => {
    return axios
        .post("registration", {
            name: newUser.name,
            email: newUser.email,
            password: newUser.password
        })
        .then(response => {
            return response.data
            console.log("Registered")
        })
}

export const login = user => {

    return axios
        .post("/", {
            email: user.email,
            password: user.password
        })
        .then(response => {
            return response.data
        })
        .catch(err => {
            console.log(err)
        })
}

export const profile = userProfile => {
    return axios
        .get("profile", )
        .then(response => {
            return response.data
        })
        .catch(err => {
            console.log(err)
        })
}

