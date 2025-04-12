import axios from 'axios';

const apiKey = 'AIzaSyDOqoLf6LIx_pFIHOePq-Neo_L2Xlw-UHk';

export const handleAddressEnter = async (address: string) => {
    try {
        const geocodeUrl = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(address)}&key=${apiKey}`;
        console.log(geocodeUrl);

        const response = await axios.get(geocodeUrl);
        const data = response.data.results[0];

        if (!data) {
            throw new Error('No results found for the given address.');
        }

        const location = data.address_components.find((component: { types: string[]; long_name: string }) =>
            component.types.includes('locality')
        )?.long_name;

        const zipcode = data.address_components.find((component: { types: string[]; long_name: string }) =>
            component.types.includes('postal_code')
        )?.long_name;

        const lat = data.geometry.location.lat;
        const lng = data.geometry.location.lng;

        return {
            location,
            zipcode,
            latitude: lat,
            longitude: lng,
        };
    } catch (error) {
        console.error('Error fetching geocode:', error);
        throw error;
    }
};